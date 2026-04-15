import io
import sqlite3
from datetime import datetime
import numpy as np
import pandas as pd
import streamlit as st
import requests
import json

# Page config
st.set_page_config(
    page_title="S&OP Forecasting Platform",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .stMain {
        background: linear-gradient(135deg, #f7f8f3 0%, #e8f5f3 100%);
    }
    h1, h2, h3 {
        color: #152238;
        font-weight: 700;
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

DB_PATH = "sop_platform.db"
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.io/api/v1/chat/completions"


def get_conn() -> sqlite3.Connection:
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db() -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            full_name TEXT NOT NULL,
            factory TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            industry TEXT,
            region TEXT,
            account_manager_username TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS sales_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            designation TEXT NOT NULL,
            month TEXT NOT NULL,
            volume INTEGER NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS market_intelligence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            headline TEXT NOT NULL,
            growth_pct REAL NOT NULL,
            source TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS forecast_lines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            designation TEXT NOT NULL,
            factory TEXT NOT NULL,
            month TEXT NOT NULL,
            input_volume INTEGER NOT NULL,
            forecast_volume INTEGER NOT NULL,
            method TEXT NOT NULL,
            growth_input REAL,
            account_manager_username TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )

    # Canonical demo seed: exactly 3 users plus expanded customer/designation data.
    # Re-seeding each startup keeps the environment deterministic for demos.
    cur.execute("DELETE FROM users")
    users = [
        ("john.wicks", "password123", "ACCOUNT_MANAGER", "John Wicks", None),
        ("rachel", "password123", "SEGMENT_HEAD", "Rachel", None),
        ("abhinav", "password123", "FACTORY_HEAD", "Abhinav", "Pune"),
    ]
    cur.executemany(
        "INSERT INTO users (username, password, role, full_name, factory) VALUES (?, ?, ?, ?, ?)",
        users,
    )

    cur.execute("DELETE FROM customers")
    customers = [
        ("Mahindra Tractors", "Tractors & Farm Equipment", "West India", "john.wicks"),
        ("Sonalika", "Tractors & Farm Equipment", "Central India", "john.wicks"),
        ("TAFE", "Tractors & Farm Equipment", "South India", "john.wicks"),
        ("Escorts Agri Machinery", "Tractors & Farm Equipment", "North India", "john.wicks"),
        ("John Deere India", "Tractors & Farm Equipment", "North India", "john.wicks"),
        ("Eicher Tractors", "Tractors & Farm Equipment", "Central India", "john.wicks"),
        ("CNH Industrial India", "Tractors & Farm Equipment", "West India", "john.wicks"),
        ("Swaraj Engines", "Tractors & Farm Equipment", "North India", "john.wicks"),
        ("Ashok Leyland", "Commercial Vehicles", "South India", "john.wicks"),
        ("Force Motors", "Commercial Vehicles", "West India", "john.wicks"),
        ("Tata Motors CV", "Commercial Vehicles", "West India", "john.wicks"),
        ("VE Commercial Vehicles", "Commercial Vehicles", "Central India", "john.wicks"),
        ("Bajaj Auto", "Two Wheelers", "West India", "john.wicks"),
        ("Hero MotoCorp", "Two Wheelers", "North India", "john.wicks"),
        ("TVS Motor", "Two Wheelers", "South India", "john.wicks"),
        ("Royal Enfield", "Two Wheelers", "South India", "john.wicks"),
        ("JCB India", "Construction Equipment", "North India", "john.wicks"),
        ("Caterpillar India", "Construction Equipment", "South India", "john.wicks"),
        ("Komatsu India", "Construction Equipment", "West India", "john.wicks"),
        ("Bosch Mobility", "Automotive Components", "South India", "john.wicks"),
    ]
    cur.executemany(
        "INSERT INTO customers (name, industry, region, account_manager_username) VALUES (?, ?, ?, ?)",
        customers,
    )

    cur.execute("DELETE FROM sales_history")
    designations = [
        "6205-2RS", "6206-ZZ", "6207-RS", "6208-2RS", "6209-ZZ", "6210-RS",
        "6211-2RS", "6301-2RS", "6302-RS", "6303-ZZ", "30205", "30206",
        "32208", "32310", "NJ205", "NU206"
    ]
    months = [
        "2024-04", "2024-05", "2024-06", "2024-07", "2024-08", "2024-09",
        "2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03",
        "2025-04", "2025-05", "2025-06", "2025-07", "2025-08", "2025-09",
        "2025-10", "2025-11", "2025-12", "2026-01", "2026-02", "2026-03",
    ]
    seasonality = [0.88, 0.91, 0.96, 1.0, 1.05, 1.09, 1.12, 1.1, 1.04, 1.0, 0.95, 0.92]

    history = []
    for c_idx, (customer_name, _, _, _) in enumerate(customers):
        start = (c_idx * 3) % len(designations)
        customer_designations = [designations[(start + i) % len(designations)] for i in range(8)]

        for d_idx, designation in enumerate(customer_designations):
            base = 180 + (c_idx * 27) + (d_idx * 35)
            for m_idx, month in enumerate(months):
                trend_factor = 1 + (0.018 * m_idx)
                season_factor = seasonality[m_idx % 12]
                volume = int(base * trend_factor * season_factor)
                history.append((customer_name, designation, month, max(volume, 80)))

    cur.executemany(
        "INSERT INTO sales_history (customer_name, designation, month, volume) VALUES (?, ?, ?, ?)",
        history,
    )

    conn.commit()
    conn.close()
    return

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        users = [
            ("john.wicks",   "password123", "ACCOUNT_MANAGER", "John Wicks",   None),
            ("priya.sharma", "password123", "ACCOUNT_MANAGER", "Priya Sharma", None),
            ("rahul.verma",  "password123", "ACCOUNT_MANAGER", "Rahul Verma",  None),
            ("rachel",       "password123", "SEGMENT_HEAD",    "Rachel",        None),
            ("abhinav",      "password123", "FACTORY_HEAD",    "Abhinav",       "Pune"),
        ]
        cur.executemany(
            "INSERT INTO users (username, password, role, full_name, factory) VALUES (?, ?, ?, ?, ?)",
            users,
        )

    cur.execute("SELECT COUNT(*) FROM customers")
    if cur.fetchone()[0] == 0:
        customers = [
            # John Wicks customers
            ("Mahindra Tractors",      "Tractors & Farm Equipment", "West India",    "john.wicks"),
            ("Sonalika",               "Tractors & Farm Equipment", "Central India", "john.wicks"),
            ("TAFE",                   "Tractors & Farm Equipment", "South India",   "john.wicks"),
            ("Escorts Agri Machinery", "Tractors & Farm Equipment", "North India",   "john.wicks"),
            # Priya Sharma customers
            ("John Deere India",       "Tractors & Farm Equipment", "North India",   "priya.sharma"),
            ("Eicher Tractors",        "Tractors & Farm Equipment", "Central India", "priya.sharma"),
            ("CNH Industrial India",   "Tractors & Farm Equipment", "West India",    "priya.sharma"),
            # Rahul Verma customers
            ("Ashok Leyland",          "Commercial Vehicles",       "South India",   "rahul.verma"),
            ("Force Motors",           "Commercial Vehicles",       "West India",    "rahul.verma"),
            ("Bajaj Auto",             "Two Wheelers",              "West India",    "rahul.verma"),
            ("Hero MotoCorp",          "Two Wheelers",              "North India",   "rahul.verma"),
        ]
        cur.executemany(
            "INSERT INTO customers (name, industry, region, account_manager_username) VALUES (?, ?, ?, ?)",
            customers,
        )

    cur.execute("SELECT COUNT(*) FROM sales_history")
    if cur.fetchone()[0] == 0:
        history = [
            # ── Mahindra Tractors ──────────────────────────────────────────────
            ("Mahindra Tractors", "6205-2RS", "2025-04", 540), ("Mahindra Tractors", "6205-2RS", "2025-05", 580),
            ("Mahindra Tractors", "6205-2RS", "2025-06", 620), ("Mahindra Tractors", "6205-2RS", "2025-07", 670),
            ("Mahindra Tractors", "6205-2RS", "2025-08", 700), ("Mahindra Tractors", "6205-2RS", "2025-09", 730),
            ("Mahindra Tractors", "6205-2RS", "2025-10", 650), ("Mahindra Tractors", "6205-2RS", "2025-11", 720),
            ("Mahindra Tractors", "6205-2RS", "2025-12", 850), ("Mahindra Tractors", "6205-2RS", "2026-01", 920),
            ("Mahindra Tractors", "6205-2RS", "2026-02", 1100),("Mahindra Tractors", "6205-2RS", "2026-03", 1250),
            ("Mahindra Tractors", "6206-ZZ",  "2025-04", 320), ("Mahindra Tractors", "6206-ZZ",  "2025-05", 360),
            ("Mahindra Tractors", "6206-ZZ",  "2025-06", 390), ("Mahindra Tractors", "6206-ZZ",  "2025-07", 410),
            ("Mahindra Tractors", "6206-ZZ",  "2025-08", 430), ("Mahindra Tractors", "6206-ZZ",  "2025-09", 440),
            ("Mahindra Tractors", "6206-ZZ",  "2025-10", 425), ("Mahindra Tractors", "6206-ZZ",  "2025-11", 480),
            ("Mahindra Tractors", "6206-ZZ",  "2025-12", 520), ("Mahindra Tractors", "6206-ZZ",  "2026-01", 650),
            ("Mahindra Tractors", "6206-ZZ",  "2026-02", 720), ("Mahindra Tractors", "6206-ZZ",  "2026-03", 800),
            ("Mahindra Tractors", "6207-RS",  "2025-04", 210), ("Mahindra Tractors", "6207-RS",  "2025-05", 240),
            ("Mahindra Tractors", "6207-RS",  "2025-06", 270), ("Mahindra Tractors", "6207-RS",  "2025-07", 290),
            ("Mahindra Tractors", "6207-RS",  "2025-08", 300), ("Mahindra Tractors", "6207-RS",  "2025-09", 310),
            ("Mahindra Tractors", "6207-RS",  "2025-10", 310), ("Mahindra Tractors", "6207-RS",  "2025-11", 360),
            ("Mahindra Tractors", "6207-RS",  "2025-12", 410), ("Mahindra Tractors", "6207-RS",  "2026-01", 480),
            ("Mahindra Tractors", "6207-RS",  "2026-02", 550), ("Mahindra Tractors", "6207-RS",  "2026-03", 620),
            ("Mahindra Tractors", "6208-2RS", "2025-04", 180), ("Mahindra Tractors", "6208-2RS", "2025-05", 200),
            ("Mahindra Tractors", "6208-2RS", "2025-06", 220), ("Mahindra Tractors", "6208-2RS", "2025-07", 245),
            ("Mahindra Tractors", "6208-2RS", "2025-08", 260), ("Mahindra Tractors", "6208-2RS", "2025-09", 275),
            ("Mahindra Tractors", "6208-2RS", "2025-10", 290), ("Mahindra Tractors", "6208-2RS", "2025-11", 320),
            ("Mahindra Tractors", "6208-2RS", "2025-12", 370), ("Mahindra Tractors", "6208-2RS", "2026-01", 420),
            ("Mahindra Tractors", "6208-2RS", "2026-02", 480), ("Mahindra Tractors", "6208-2RS", "2026-03", 540),
            ("Mahindra Tractors", "30205",    "2025-04", 140), ("Mahindra Tractors", "30205",    "2025-05", 155),
            ("Mahindra Tractors", "30205",    "2025-06", 170), ("Mahindra Tractors", "30205",    "2025-07", 185),
            ("Mahindra Tractors", "30205",    "2025-08", 200), ("Mahindra Tractors", "30205",    "2025-09", 215),
            ("Mahindra Tractors", "30205",    "2025-10", 230), ("Mahindra Tractors", "30205",    "2025-11", 260),
            ("Mahindra Tractors", "30205",    "2025-12", 300), ("Mahindra Tractors", "30205",    "2026-01", 340),
            ("Mahindra Tractors", "30205",    "2026-02", 390), ("Mahindra Tractors", "30205",    "2026-03", 440),
            # ── Sonalika ──────────────────────────────────────────────────────
            ("Sonalika", "6205-2RS", "2025-04", 410), ("Sonalika", "6205-2RS", "2025-05", 450),
            ("Sonalika", "6205-2RS", "2025-06", 490), ("Sonalika", "6205-2RS", "2025-07", 520),
            ("Sonalika", "6205-2RS", "2025-08", 545), ("Sonalika", "6205-2RS", "2025-09", 560),
            ("Sonalika", "6205-2RS", "2025-10", 520), ("Sonalika", "6205-2RS", "2025-11", 580),
            ("Sonalika", "6205-2RS", "2025-12", 650), ("Sonalika", "6205-2RS", "2026-01", 720),
            ("Sonalika", "6205-2RS", "2026-02", 800), ("Sonalika", "6205-2RS", "2026-03", 920),
            ("Sonalika", "6206-ZZ",  "2025-04", 280), ("Sonalika", "6206-ZZ",  "2025-05", 310),
            ("Sonalika", "6206-ZZ",  "2025-06", 340), ("Sonalika", "6206-ZZ",  "2025-07", 365),
            ("Sonalika", "6206-ZZ",  "2025-08", 375), ("Sonalika", "6206-ZZ",  "2025-09", 380),
            ("Sonalika", "6206-ZZ",  "2025-10", 380), ("Sonalika", "6206-ZZ",  "2025-11", 420),
            ("Sonalika", "6206-ZZ",  "2025-12", 480), ("Sonalika", "6206-ZZ",  "2026-01", 540),
            ("Sonalika", "6206-ZZ",  "2026-02", 620), ("Sonalika", "6206-ZZ",  "2026-03", 680),
            ("Sonalika", "6207-RS",  "2025-04", 170), ("Sonalika", "6207-RS",  "2025-05", 195),
            ("Sonalika", "6207-RS",  "2025-06", 215), ("Sonalika", "6207-RS",  "2025-07", 235),
            ("Sonalika", "6207-RS",  "2025-08", 245), ("Sonalika", "6207-RS",  "2025-09", 250),
            ("Sonalika", "6207-RS",  "2025-10", 250), ("Sonalika", "6207-RS",  "2025-11", 290),
            ("Sonalika", "6207-RS",  "2025-12", 340), ("Sonalika", "6207-RS",  "2026-01", 410),
            ("Sonalika", "6207-RS",  "2026-02", 480), ("Sonalika", "6207-RS",  "2026-03", 550),
            ("Sonalika", "6209-ZZ",  "2025-04", 120), ("Sonalika", "6209-ZZ",  "2025-05", 135),
            ("Sonalika", "6209-ZZ",  "2025-06", 150), ("Sonalika", "6209-ZZ",  "2025-07", 168),
            ("Sonalika", "6209-ZZ",  "2025-08", 180), ("Sonalika", "6209-ZZ",  "2025-09", 190),
            ("Sonalika", "6209-ZZ",  "2025-10", 200), ("Sonalika", "6209-ZZ",  "2025-11", 225),
            ("Sonalika", "6209-ZZ",  "2025-12", 260), ("Sonalika", "6209-ZZ",  "2026-01", 300),
            ("Sonalika", "6209-ZZ",  "2026-02", 345), ("Sonalika", "6209-ZZ",  "2026-03", 390),
            ("Sonalika", "30205",    "2025-04", 100), ("Sonalika", "30205",    "2025-05", 115),
            ("Sonalika", "30205",    "2025-06", 125), ("Sonalika", "30205",    "2025-07", 138),
            ("Sonalika", "30205",    "2025-08", 150), ("Sonalika", "30205",    "2025-09", 160),
            ("Sonalika", "30205",    "2025-10", 170), ("Sonalika", "30205",    "2025-11", 195),
            ("Sonalika", "30205",    "2025-12", 225), ("Sonalika", "30205",    "2026-01", 260),
            ("Sonalika", "30205",    "2026-02", 295), ("Sonalika", "30205",    "2026-03", 335),
            # ── TAFE ──────────────────────────────────────────────────────────
            ("TAFE", "6205-2RS", "2025-04", 330), ("TAFE", "6205-2RS", "2025-05", 365),
            ("TAFE", "6205-2RS", "2025-06", 395), ("TAFE", "6205-2RS", "2025-07", 420),
            ("TAFE", "6205-2RS", "2025-08", 440), ("TAFE", "6205-2RS", "2025-09", 450),
            ("TAFE", "6205-2RS", "2025-10", 420), ("TAFE", "6205-2RS", "2025-11", 480),
            ("TAFE", "6205-2RS", "2025-12", 540), ("TAFE", "6205-2RS", "2026-01", 620),
            ("TAFE", "6205-2RS", "2026-02", 680), ("TAFE", "6205-2RS", "2026-03", 750),
            ("TAFE", "6206-ZZ",  "2025-04", 230), ("TAFE", "6206-ZZ",  "2025-05", 258),
            ("TAFE", "6206-ZZ",  "2025-06", 280), ("TAFE", "6206-ZZ",  "2025-07", 295),
            ("TAFE", "6206-ZZ",  "2025-08", 305), ("TAFE", "6206-ZZ",  "2025-09", 310),
            ("TAFE", "6206-ZZ",  "2025-10", 310), ("TAFE", "6206-ZZ",  "2025-11", 350),
            ("TAFE", "6206-ZZ",  "2025-12", 400), ("TAFE", "6206-ZZ",  "2026-01", 480),
            ("TAFE", "6206-ZZ",  "2026-02", 540), ("TAFE", "6206-ZZ",  "2026-03", 600),
            ("TAFE", "6207-RS",  "2025-04", 140), ("TAFE", "6207-RS",  "2025-05", 162),
            ("TAFE", "6207-RS",  "2025-06", 180), ("TAFE", "6207-RS",  "2025-07", 196),
            ("TAFE", "6207-RS",  "2025-08", 205), ("TAFE", "6207-RS",  "2025-09", 210),
            ("TAFE", "6207-RS",  "2025-10", 200), ("TAFE", "6207-RS",  "2025-11", 240),
            ("TAFE", "6207-RS",  "2025-12", 290), ("TAFE", "6207-RS",  "2026-01", 350),
            ("TAFE", "6207-RS",  "2026-02", 410), ("TAFE", "6207-RS",  "2026-03", 480),
            ("TAFE", "6210-RS",  "2025-04", 95),  ("TAFE", "6210-RS",  "2025-05", 108),
            ("TAFE", "6210-RS",  "2025-06", 120), ("TAFE", "6210-RS",  "2025-07", 132),
            ("TAFE", "6210-RS",  "2025-08", 142), ("TAFE", "6210-RS",  "2025-09", 150),
            ("TAFE", "6210-RS",  "2025-10", 158), ("TAFE", "6210-RS",  "2025-11", 178),
            ("TAFE", "6210-RS",  "2025-12", 205), ("TAFE", "6210-RS",  "2026-01", 235),
            ("TAFE", "6210-RS",  "2026-02", 270), ("TAFE", "6210-RS",  "2026-03", 310),
            # ── Escorts Agri Machinery ────────────────────────────────────────
            ("Escorts Agri Machinery", "6205-2RS", "2025-04", 290), ("Escorts Agri Machinery", "6205-2RS", "2025-05", 320),
            ("Escorts Agri Machinery", "6205-2RS", "2025-06", 350), ("Escorts Agri Machinery", "6205-2RS", "2025-07", 375),
            ("Escorts Agri Machinery", "6205-2RS", "2025-08", 395), ("Escorts Agri Machinery", "6205-2RS", "2025-09", 410),
            ("Escorts Agri Machinery", "6205-2RS", "2025-10", 430), ("Escorts Agri Machinery", "6205-2RS", "2025-11", 470),
            ("Escorts Agri Machinery", "6205-2RS", "2025-12", 520), ("Escorts Agri Machinery", "6205-2RS", "2026-01", 580),
            ("Escorts Agri Machinery", "6205-2RS", "2026-02", 640), ("Escorts Agri Machinery", "6205-2RS", "2026-03", 710),
            ("Escorts Agri Machinery", "6206-ZZ",  "2025-04", 200), ("Escorts Agri Machinery", "6206-ZZ",  "2025-05", 220),
            ("Escorts Agri Machinery", "6206-ZZ",  "2025-06", 240), ("Escorts Agri Machinery", "6206-ZZ",  "2025-07", 258),
            ("Escorts Agri Machinery", "6206-ZZ",  "2025-08", 270), ("Escorts Agri Machinery", "6206-ZZ",  "2025-09", 278),
            ("Escorts Agri Machinery", "6206-ZZ",  "2025-10", 285), ("Escorts Agri Machinery", "6206-ZZ",  "2025-11", 315),
            ("Escorts Agri Machinery", "6206-ZZ",  "2025-12", 360), ("Escorts Agri Machinery", "6206-ZZ",  "2026-01", 410),
            ("Escorts Agri Machinery", "6206-ZZ",  "2026-02", 460), ("Escorts Agri Machinery", "6206-ZZ",  "2026-03", 510),
            ("Escorts Agri Machinery", "6301-2RS", "2025-04", 160), ("Escorts Agri Machinery", "6301-2RS", "2025-05", 178),
            ("Escorts Agri Machinery", "6301-2RS", "2025-06", 195), ("Escorts Agri Machinery", "6301-2RS", "2025-07", 210),
            ("Escorts Agri Machinery", "6301-2RS", "2025-08", 222), ("Escorts Agri Machinery", "6301-2RS", "2025-09", 230),
            ("Escorts Agri Machinery", "6301-2RS", "2025-10", 240), ("Escorts Agri Machinery", "6301-2RS", "2025-11", 268),
            ("Escorts Agri Machinery", "6301-2RS", "2025-12", 305), ("Escorts Agri Machinery", "6301-2RS", "2026-01", 348),
            ("Escorts Agri Machinery", "6301-2RS", "2026-02", 395), ("Escorts Agri Machinery", "6301-2RS", "2026-03", 445),
            # ── John Deere India ──────────────────────────────────────────────
            ("John Deere India", "6205-2RS", "2025-04", 520), ("John Deere India", "6205-2RS", "2025-05", 565),
            ("John Deere India", "6205-2RS", "2025-06", 610), ("John Deere India", "6205-2RS", "2025-07", 650),
            ("John Deere India", "6205-2RS", "2025-08", 680), ("John Deere India", "6205-2RS", "2025-09", 700),
            ("John Deere India", "6205-2RS", "2025-10", 720), ("John Deere India", "6205-2RS", "2025-11", 780),
            ("John Deere India", "6205-2RS", "2025-12", 860), ("John Deere India", "6205-2RS", "2026-01", 950),
            ("John Deere India", "6205-2RS", "2026-02", 1050),("John Deere India", "6205-2RS", "2026-03", 1160),
            ("John Deere India", "6208-2RS", "2025-04", 380), ("John Deere India", "6208-2RS", "2025-05", 415),
            ("John Deere India", "6208-2RS", "2025-06", 450), ("John Deere India", "6208-2RS", "2025-07", 480),
            ("John Deere India", "6208-2RS", "2025-08", 505), ("John Deere India", "6208-2RS", "2025-09", 520),
            ("John Deere India", "6208-2RS", "2025-10", 540), ("John Deere India", "6208-2RS", "2025-11", 590),
            ("John Deere India", "6208-2RS", "2025-12", 655), ("John Deere India", "6208-2RS", "2026-01", 730),
            ("John Deere India", "6208-2RS", "2026-02", 810), ("John Deere India", "6208-2RS", "2026-03", 900),
            ("John Deere India", "30205",    "2025-04", 260), ("John Deere India", "30205",    "2025-05", 285),
            ("John Deere India", "30205",    "2025-06", 310), ("John Deere India", "30205",    "2025-07", 332),
            ("John Deere India", "30205",    "2025-08", 350), ("John Deere India", "30205",    "2025-09", 362),
            ("John Deere India", "30205",    "2025-10", 375), ("John Deere India", "30205",    "2025-11", 410),
            ("John Deere India", "30205",    "2025-12", 460), ("John Deere India", "30205",    "2026-01", 515),
            ("John Deere India", "30205",    "2026-02", 575), ("John Deere India", "30205",    "2026-03", 640),
            # ── Eicher Tractors ───────────────────────────────────────────────
            ("Eicher Tractors", "6205-2RS", "2025-04", 350), ("Eicher Tractors", "6205-2RS", "2025-05", 385),
            ("Eicher Tractors", "6205-2RS", "2025-06", 415), ("Eicher Tractors", "6205-2RS", "2025-07", 440),
            ("Eicher Tractors", "6205-2RS", "2025-08", 460), ("Eicher Tractors", "6205-2RS", "2025-09", 475),
            ("Eicher Tractors", "6205-2RS", "2025-10", 490), ("Eicher Tractors", "6205-2RS", "2025-11", 535),
            ("Eicher Tractors", "6205-2RS", "2025-12", 595), ("Eicher Tractors", "6205-2RS", "2026-01", 660),
            ("Eicher Tractors", "6205-2RS", "2026-02", 730), ("Eicher Tractors", "6205-2RS", "2026-03", 810),
            ("Eicher Tractors", "6207-RS",  "2025-04", 220), ("Eicher Tractors", "6207-RS",  "2025-05", 245),
            ("Eicher Tractors", "6207-RS",  "2025-06", 267), ("Eicher Tractors", "6207-RS",  "2025-07", 285),
            ("Eicher Tractors", "6207-RS",  "2025-08", 298), ("Eicher Tractors", "6207-RS",  "2025-09", 308),
            ("Eicher Tractors", "6207-RS",  "2025-10", 318), ("Eicher Tractors", "6207-RS",  "2025-11", 350),
            ("Eicher Tractors", "6207-RS",  "2025-12", 395), ("Eicher Tractors", "6207-RS",  "2026-01", 445),
            ("Eicher Tractors", "6207-RS",  "2026-02", 500), ("Eicher Tractors", "6207-RS",  "2026-03", 558),
            ("Eicher Tractors", "6303-ZZ",  "2025-04", 130), ("Eicher Tractors", "6303-ZZ",  "2025-05", 145),
            ("Eicher Tractors", "6303-ZZ",  "2025-06", 158), ("Eicher Tractors", "6303-ZZ",  "2025-07", 170),
            ("Eicher Tractors", "6303-ZZ",  "2025-08", 180), ("Eicher Tractors", "6303-ZZ",  "2025-09", 187),
            ("Eicher Tractors", "6303-ZZ",  "2025-10", 195), ("Eicher Tractors", "6303-ZZ",  "2025-11", 218),
            ("Eicher Tractors", "6303-ZZ",  "2025-12", 250), ("Eicher Tractors", "6303-ZZ",  "2026-01", 285),
            ("Eicher Tractors", "6303-ZZ",  "2026-02", 325), ("Eicher Tractors", "6303-ZZ",  "2026-03", 368),
            # ── CNH Industrial India ──────────────────────────────────────────
            ("CNH Industrial India", "6205-2RS", "2025-04", 310), ("CNH Industrial India", "6205-2RS", "2025-05", 340),
            ("CNH Industrial India", "6205-2RS", "2025-06", 368), ("CNH Industrial India", "6205-2RS", "2025-07", 392),
            ("CNH Industrial India", "6205-2RS", "2025-08", 410), ("CNH Industrial India", "6205-2RS", "2025-09", 422),
            ("CNH Industrial India", "6205-2RS", "2025-10", 435), ("CNH Industrial India", "6205-2RS", "2025-11", 475),
            ("CNH Industrial India", "6205-2RS", "2025-12", 528), ("CNH Industrial India", "6205-2RS", "2026-01", 585),
            ("CNH Industrial India", "6205-2RS", "2026-02", 648), ("CNH Industrial India", "6205-2RS", "2026-03", 718),
            ("CNH Industrial India", "6208-2RS", "2025-04", 195), ("CNH Industrial India", "6208-2RS", "2025-05", 215),
            ("CNH Industrial India", "6208-2RS", "2025-06", 234), ("CNH Industrial India", "6208-2RS", "2025-07", 250),
            ("CNH Industrial India", "6208-2RS", "2025-08", 263), ("CNH Industrial India", "6208-2RS", "2025-09", 272),
            ("CNH Industrial India", "6208-2RS", "2025-10", 282), ("CNH Industrial India", "6208-2RS", "2025-11", 308),
            ("CNH Industrial India", "6208-2RS", "2025-12", 345), ("CNH Industrial India", "6208-2RS", "2026-01", 388),
            ("CNH Industrial India", "6208-2RS", "2026-02", 435), ("CNH Industrial India", "6208-2RS", "2026-03", 488),
            ("CNH Industrial India", "6301-2RS", "2025-04", 140), ("CNH Industrial India", "6301-2RS", "2025-05", 155),
            ("CNH Industrial India", "6301-2RS", "2025-06", 170), ("CNH Industrial India", "6301-2RS", "2025-07", 182),
            ("CNH Industrial India", "6301-2RS", "2025-08", 192), ("CNH Industrial India", "6301-2RS", "2025-09", 200),
            ("CNH Industrial India", "6301-2RS", "2025-10", 208), ("CNH Industrial India", "6301-2RS", "2025-11", 228),
            ("CNH Industrial India", "6301-2RS", "2025-12", 258), ("CNH Industrial India", "6301-2RS", "2026-01", 292),
            ("CNH Industrial India", "6301-2RS", "2026-02", 330), ("CNH Industrial India", "6301-2RS", "2026-03", 372),
            # ── Ashok Leyland ─────────────────────────────────────────────────
            ("Ashok Leyland", "6209-ZZ",  "2025-04", 460), ("Ashok Leyland", "6209-ZZ",  "2025-05", 500),
            ("Ashok Leyland", "6209-ZZ",  "2025-06", 540), ("Ashok Leyland", "6209-ZZ",  "2025-07", 575),
            ("Ashok Leyland", "6209-ZZ",  "2025-08", 602), ("Ashok Leyland", "6209-ZZ",  "2025-09", 622),
            ("Ashok Leyland", "6209-ZZ",  "2025-10", 640), ("Ashok Leyland", "6209-ZZ",  "2025-11", 695),
            ("Ashok Leyland", "6209-ZZ",  "2025-12", 768), ("Ashok Leyland", "6209-ZZ",  "2026-01", 850),
            ("Ashok Leyland", "6209-ZZ",  "2026-02", 940), ("Ashok Leyland", "6209-ZZ",  "2026-03", 1040),
            ("Ashok Leyland", "6210-RS",  "2025-04", 340), ("Ashok Leyland", "6210-RS",  "2025-05", 372),
            ("Ashok Leyland", "6210-RS",  "2025-06", 402), ("Ashok Leyland", "6210-RS",  "2025-07", 428),
            ("Ashok Leyland", "6210-RS",  "2025-08", 449), ("Ashok Leyland", "6210-RS",  "2025-09", 464),
            ("Ashok Leyland", "6210-RS",  "2025-10", 478), ("Ashok Leyland", "6210-RS",  "2025-11", 520),
            ("Ashok Leyland", "6210-RS",  "2025-12", 578), ("Ashok Leyland", "6210-RS",  "2026-01", 643),
            ("Ashok Leyland", "6210-RS",  "2026-02", 715), ("Ashok Leyland", "6210-RS",  "2026-03", 796),
            ("Ashok Leyland", "30205",    "2025-04", 280), ("Ashok Leyland", "30205",    "2025-05", 308),
            ("Ashok Leyland", "30205",    "2025-06", 333), ("Ashok Leyland", "30205",    "2025-07", 355),
            ("Ashok Leyland", "30205",    "2025-08", 372), ("Ashok Leyland", "30205",    "2025-09", 385),
            ("Ashok Leyland", "30205",    "2025-10", 398), ("Ashok Leyland", "30205",    "2025-11", 433),
            ("Ashok Leyland", "30205",    "2025-12", 482), ("Ashok Leyland", "30205",    "2026-01", 537),
            ("Ashok Leyland", "30205",    "2026-02", 598), ("Ashok Leyland", "30205",    "2026-03", 665),
            # ── Force Motors ──────────────────────────────────────────────────
            ("Force Motors", "6208-2RS", "2025-04", 260), ("Force Motors", "6208-2RS", "2025-05", 285),
            ("Force Motors", "6208-2RS", "2025-06", 308), ("Force Motors", "6208-2RS", "2025-07", 328),
            ("Force Motors", "6208-2RS", "2025-08", 344), ("Force Motors", "6208-2RS", "2025-09", 356),
            ("Force Motors", "6208-2RS", "2025-10", 368), ("Force Motors", "6208-2RS", "2025-11", 400),
            ("Force Motors", "6208-2RS", "2025-12", 446), ("Force Motors", "6208-2RS", "2026-01", 498),
            ("Force Motors", "6208-2RS", "2026-02", 554), ("Force Motors", "6208-2RS", "2026-03", 616),
            ("Force Motors", "6209-ZZ",  "2025-04", 190), ("Force Motors", "6209-ZZ",  "2025-05", 210),
            ("Force Motors", "6209-ZZ",  "2025-06", 228), ("Force Motors", "6209-ZZ",  "2025-07", 244),
            ("Force Motors", "6209-ZZ",  "2025-08", 256), ("Force Motors", "6209-ZZ",  "2025-09", 265),
            ("Force Motors", "6209-ZZ",  "2025-10", 274), ("Force Motors", "6209-ZZ",  "2025-11", 299),
            ("Force Motors", "6209-ZZ",  "2025-12", 334), ("Force Motors", "6209-ZZ",  "2026-01", 374),
            ("Force Motors", "6209-ZZ",  "2026-02", 418), ("Force Motors", "6209-ZZ",  "2026-03", 466),
            ("Force Motors", "6303-ZZ",  "2025-04", 115), ("Force Motors", "6303-ZZ",  "2025-05", 128),
            ("Force Motors", "6303-ZZ",  "2025-06", 140), ("Force Motors", "6303-ZZ",  "2025-07", 150),
            ("Force Motors", "6303-ZZ",  "2025-08", 158), ("Force Motors", "6303-ZZ",  "2025-09", 164),
            ("Force Motors", "6303-ZZ",  "2025-10", 170), ("Force Motors", "6303-ZZ",  "2025-11", 186),
            ("Force Motors", "6303-ZZ",  "2025-12", 208), ("Force Motors", "6303-ZZ",  "2026-01", 234),
            ("Force Motors", "6303-ZZ",  "2026-02", 262), ("Force Motors", "6303-ZZ",  "2026-03", 293),
            # ── Bajaj Auto ────────────────────────────────────────────────────
            ("Bajaj Auto", "6301-2RS", "2025-04", 680), ("Bajaj Auto", "6301-2RS", "2025-05", 740),
            ("Bajaj Auto", "6301-2RS", "2025-06", 800), ("Bajaj Auto", "6301-2RS", "2025-07", 850),
            ("Bajaj Auto", "6301-2RS", "2025-08", 892), ("Bajaj Auto", "6301-2RS", "2025-09", 922),
            ("Bajaj Auto", "6301-2RS", "2025-10", 950), ("Bajaj Auto", "6301-2RS", "2025-11", 1020),
            ("Bajaj Auto", "6301-2RS", "2025-12", 1110),("Bajaj Auto", "6301-2RS", "2026-01", 1210),
            ("Bajaj Auto", "6301-2RS", "2026-02", 1320),("Bajaj Auto", "6301-2RS", "2026-03", 1440),
            ("Bajaj Auto", "6303-ZZ",  "2025-04", 510), ("Bajaj Auto", "6303-ZZ",  "2025-05", 558),
            ("Bajaj Auto", "6303-ZZ",  "2025-06", 604), ("Bajaj Auto", "6303-ZZ",  "2025-07", 643),
            ("Bajaj Auto", "6303-ZZ",  "2025-08", 675), ("Bajaj Auto", "6303-ZZ",  "2025-09", 698),
            ("Bajaj Auto", "6303-ZZ",  "2025-10", 720), ("Bajaj Auto", "6303-ZZ",  "2025-11", 778),
            ("Bajaj Auto", "6303-ZZ",  "2025-12", 856), ("Bajaj Auto", "6303-ZZ",  "2026-01", 945),
            ("Bajaj Auto", "6303-ZZ",  "2026-02", 1044),("Bajaj Auto", "6303-ZZ",  "2026-03", 1154),
            ("Bajaj Auto", "6205-2RS", "2025-04", 390), ("Bajaj Auto", "6205-2RS", "2025-05", 428),
            ("Bajaj Auto", "6205-2RS", "2025-06", 464), ("Bajaj Auto", "6205-2RS", "2025-07", 496),
            ("Bajaj Auto", "6205-2RS", "2025-08", 522), ("Bajaj Auto", "6205-2RS", "2025-09", 541),
            ("Bajaj Auto", "6205-2RS", "2025-10", 558), ("Bajaj Auto", "6205-2RS", "2025-11", 604),
            ("Bajaj Auto", "6205-2RS", "2025-12", 668), ("Bajaj Auto", "6205-2RS", "2026-01", 742),
            ("Bajaj Auto", "6205-2RS", "2026-02", 824), ("Bajaj Auto", "6205-2RS", "2026-03", 916),
            # ── Hero MotoCorp ─────────────────────────────────────────────────
            ("Hero MotoCorp", "6301-2RS", "2025-04", 820), ("Hero MotoCorp", "6301-2RS", "2025-05", 890),
            ("Hero MotoCorp", "6301-2RS", "2025-06", 960), ("Hero MotoCorp", "6301-2RS", "2025-07", 1020),
            ("Hero MotoCorp", "6301-2RS", "2025-08", 1070),("Hero MotoCorp", "6301-2RS", "2025-09", 1105),
            ("Hero MotoCorp", "6301-2RS", "2025-10", 1140),("Hero MotoCorp", "6301-2RS", "2025-11", 1220),
            ("Hero MotoCorp", "6301-2RS", "2025-12", 1330),("Hero MotoCorp", "6301-2RS", "2026-01", 1450),
            ("Hero MotoCorp", "6301-2RS", "2026-02", 1580),("Hero MotoCorp", "6301-2RS", "2026-03", 1720),
            ("Hero MotoCorp", "6303-ZZ",  "2025-04", 620), ("Hero MotoCorp", "6303-ZZ",  "2025-05", 675),
            ("Hero MotoCorp", "6303-ZZ",  "2025-06", 729), ("Hero MotoCorp", "6303-ZZ",  "2025-07", 776),
            ("Hero MotoCorp", "6303-ZZ",  "2025-08", 815), ("Hero MotoCorp", "6303-ZZ",  "2025-09", 843),
            ("Hero MotoCorp", "6303-ZZ",  "2025-10", 870), ("Hero MotoCorp", "6303-ZZ",  "2025-11", 940),
            ("Hero MotoCorp", "6303-ZZ",  "2025-12", 1030),("Hero MotoCorp", "6303-ZZ",  "2026-01", 1130),
            ("Hero MotoCorp", "6303-ZZ",  "2026-02", 1240),("Hero MotoCorp", "6303-ZZ",  "2026-03", 1360),
            ("Hero MotoCorp", "6209-ZZ",  "2025-04", 430), ("Hero MotoCorp", "6209-ZZ",  "2025-05", 470),
            ("Hero MotoCorp", "6209-ZZ",  "2025-06", 508), ("Hero MotoCorp", "6209-ZZ",  "2025-07", 542),
            ("Hero MotoCorp", "6209-ZZ",  "2025-08", 569), ("Hero MotoCorp", "6209-ZZ",  "2025-09", 589),
            ("Hero MotoCorp", "6209-ZZ",  "2025-10", 608), ("Hero MotoCorp", "6209-ZZ",  "2025-11", 658),
            ("Hero MotoCorp", "6209-ZZ",  "2025-12", 726), ("Hero MotoCorp", "6209-ZZ",  "2026-01", 805),
            ("Hero MotoCorp", "6209-ZZ",  "2026-02", 892), ("Hero MotoCorp", "6209-ZZ",  "2026-03", 990),
        ]
        cur.executemany(
            "INSERT INTO sales_history (customer_name, designation, month, volume) VALUES (?, ?, ?, ?)",
            history,
        )

    conn.commit()
    conn.close()


def generate_market_intelligence(customer_name: str, industry: str, region: str) -> dict:
    """Use OpenRouter API to generate market intelligence"""
    try:
        prompt = f"""You are a market intelligence expert for the bearing and automotive industry.
Based on: {customer_name} ({industry}, {region})
Generate 2-3 realistic growth insights as JSON:
[{{"headline": "insight text", "growth_pct": 8}}, {{"headline": "insight text", "growth_pct": 12}}]
Only return JSON, no other text."""

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://bluetext.dev"
        }

        data = {
            "model": "mistralai/mistral-7b-instruct:free",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(OPENROUTER_API_URL, json=data, headers=headers, timeout=15)
        response.raise_for_status()
        
        result = response.json()
        if result.get("choices") and len(result["choices"]) > 0:
            content = result["choices"][0]["message"]["content"]
            # Extract JSON from response
            import re
            json_match = re.search(r'\[.*?\]', content, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
            else:
                insights = json.loads(content)
            return {"success": True, "insights": insights}
    except Exception as e:
        # Fallback: generate realistic mock insights
        mock_insights = [
            {"headline": f"{customer_name} expanding production capacity by 15% in {region} region", "growth_pct": 15},
            {"headline": f"{industry} sector seeing strong demand for precision bearings amid infrastructure growth", "growth_pct": 12},
            {"headline": f"Government policies boosting {industry} manufacturing in {region}, demand expected to rise", "growth_pct": 9}
        ]
        return {"success": True, "insights": mock_insights, "source": "Simulated"}
    
    return {"success": False, "error": "Unknown error"}


def save_market_intelligence(customer_name: str, insights: list) -> None:
    """Save AI-generated market intelligence to database"""
    conn = get_conn()
    cur = conn.cursor()
    timestamp = datetime.now().isoformat()
    
    for insight in insights:
        cur.execute(
            """INSERT INTO market_intelligence (customer_name, headline, growth_pct, source, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (customer_name, insight["headline"], insight.get("growth_pct", 0), insight.get("source", "AI-Generated"), timestamp)
        )
    
    conn.commit()
    conn.close()


def get_customer_market_intelligence(customer_name: str) -> pd.DataFrame:
    """Get market intelligence for a customer"""
    conn = get_conn()
    query = "SELECT headline, growth_pct, source, created_at FROM market_intelligence WHERE customer_name = ? ORDER BY created_at DESC LIMIT 5"
    df = pd.read_sql_query(query, conn, params=(customer_name,))
    conn.close()
    return df


def get_sales_history(customer_name: str = None) -> pd.DataFrame:
    """Get sales history"""
    conn = get_conn()
    if customer_name:
        query = "SELECT customer_name, designation, month, volume FROM sales_history WHERE customer_name = ? ORDER BY month DESC"
        df = pd.read_sql_query(query, conn, params=(customer_name,))
    else:
        query = "SELECT customer_name, designation, month, volume FROM sales_history ORDER BY month DESC"
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def get_all_customers() -> list:
    """Get all customers"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name FROM customers ORDER BY name")
    customers = [row[0] for row in cur.fetchall()]
    conn.close()
    return customers


def get_customer_info(customer_name: str) -> dict:
    """Get customer details"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT name, industry, region FROM customers WHERE name = ?", (customer_name,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"name": row[0], "industry": row[1], "region": row[2]}
    return None


def get_all_designations() -> list:
    """Get all unique bearing designations"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT designation FROM sales_history ORDER BY designation")
    designations = [row[0] for row in cur.fetchall()]
    conn.close()
    return designations


def get_filtered_sales_data(customers: list, designations: list) -> pd.DataFrame:
    """Get filtered sales data by customers and designations"""
    conn = get_conn()
    
    placeholders_cust = ','.join('?' * len(customers))
    placeholders_des = ','.join('?' * len(designations))
    
    query = f"""
        SELECT customer_name, designation, month, volume 
        FROM sales_history 
        WHERE customer_name IN ({placeholders_cust}) 
        AND designation IN ({placeholders_des})
        ORDER BY month DESC
    """
    
    df = pd.read_sql_query(query, conn, params=customers + designations)
    conn.close()
    return df


def get_forecast_statistics() -> dict:
    """Get forecast statistics"""
    conn = get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) FROM forecast_lines")
    total_forecasts = cur.fetchone()[0]
    
    cur.execute("SELECT SUM(forecast_volume) FROM forecast_lines")
    total_volume = cur.fetchone()[0] or 0
    
    cur.execute("SELECT COUNT(DISTINCT customer_name) FROM forecast_lines")
    unique_customers = cur.fetchone()[0]
    
    conn.close()
    
    return {
        "total_forecasts": total_forecasts,
        "total_volume": total_volume,
        "unique_customers": unique_customers
    }


def save_forecast(customer: str, designation: str, factory: str, month: str, 
                 input_vol: int, forecast_vol: int, method: str, growth: float = None) -> None:
    """Save forecast to database"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO forecast_lines (customer_name, designation, factory, month, 
           input_volume, forecast_volume, method, growth_input, account_manager_username, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (customer, designation, factory, month, input_vol, forecast_vol, method, growth, "john.wicks", datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


def login_page():
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("##  S&OP Forecasting Engine")
        st.markdown("### AI-Driven Planning System")
        
        st.divider()
        
        username = st.text_input("👤 Username", value="")
        password = st.text_input("🔑 Password", type="password", value="")
        
        if st.button("Sign In", type="primary", use_container_width=True):
            conn = get_conn()
            cur = conn.cursor()
            cur.execute("SELECT id, role, full_name FROM users WHERE username = ? AND password = ?", 
                       (username, password))
            user = cur.fetchone()
            conn.close()
            
            if user:
                st.session_state.user_id = user[0]
                st.session_state.user_role = user[1]
                st.session_state.user_name = user[2]
                st.session_state.username = username
                st.session_state.authenticated = True
                st.success(f"Welcome, {user[2]}! 👋")
                st.rerun()
            else:
                st.error("❌ Invalid credentials")
        
       


def account_manager_page():
    st.title("Account Manager Dashboard")
    st.markdown(f"Welcome, **{st.session_state.user_name}** | Manage forecasts and customer insights")
    
    # Enhanced styling
    st.markdown("""
    <style>
        .forecast-success {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
    
    stats = get_forecast_statistics()
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Forecasts", stats["total_forecasts"])
    col2.metric("Total Volume", f"{stats['total_volume']:,.0f}")
    col3.metric("Customers", stats["unique_customers"])
    col4.metric("Status", "Active")
    col5.metric("Target", "100%")
    
    st.divider()
    
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("📋 Generate Forecast")
        
        customers = get_all_customers()
        selected_customer = st.selectbox("Select Customer", customers, key="am_customer")
        
        if selected_customer:
            customer_info = get_customer_info(selected_customer)
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        padding: 10px; border-radius: 8px; color: white;'>
            <b>🏢 {customer_info['industry']}</b> | <b> {customer_info['region']}</b>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("#### 💡 Market Intelligence")
        
        if selected_customer:
            intel_df = get_customer_market_intelligence(selected_customer)
            
            if len(intel_df) == 0:
                if st.button("Generate AI Market Insights", key="gen_intel_am"):
                    with st.spinner("Analyzing market..."):
                        result = generate_market_intelligence(
                            selected_customer,
                            customer_info["industry"],
                            customer_info["region"]
                        )
                        if result["success"]:
                            source = result.get("source", "AI-Generated")
                            for ins in result["insights"]:
                                ins.setdefault("source", source)
                            save_market_intelligence(selected_customer, result["insights"])
                            st.success("✅ Market insights generated!")
                            st.rerun()
                        else:
                            st.error(f"⚠️ {result.get('error', 'Failed')}")
            else:
                for _, row in intel_df.iterrows():
                    st.success(f"📰 {row['headline']} (+{row['growth_pct']:.0f}%)")
        
        designation = st.text_input("Bearing Designation", value="6205-2RS", key="am_desig")
        factory = st.selectbox("Factory", ["Pune", "Chennai", "Bangalore"], key="am_factory")
    
    with col2:
        st.subheader(" Forecast Parameters")
        
        month = st.text_input("Month (YYYY-MM)", value="2026-05", key="am_month")
        input_volume = st.number_input("Input Volume", min_value=100, value=1000, step=100, key="am_vol")
        growth_percent = st.slider("Growth % Adjustment", -20, 50, 10, key="am_growth")
        
        st.divider()
        
        st.subheader(" Method Selection")
        method = st.radio("Select Forecasting Method", ["Sales History", "User Growth Input", "Market Intelligence"], 
                          horizontal=True, key="am_method")
        
        if st.button("Generate Forecast", type="primary", use_container_width=True, key="am_forecast_btn"):
            if selected_customer and designation and factory and month:
                if method == "Sales History":
                    forecast_vol = int(input_volume * 1.05)
                elif method == "User Growth Input":
                    forecast_vol = int(input_volume * (1 + growth_percent / 100))
                else:
                    intel_df = get_customer_market_intelligence(selected_customer)
                    growth_boost = intel_df["growth_pct"].mean() / 100 if len(intel_df) > 0 else 0.08
                    forecast_vol = int(input_volume * (1 + growth_percent / 100 + growth_boost))
                
                save_forecast(selected_customer, designation, factory, month, input_volume, forecast_vol, method, growth_percent)
                st.markdown(f"<div class='forecast-success'><b> Forecast saved!</b><br>Volume: {forecast_vol:,} units</div>", unsafe_allow_html=True)
    
    st.divider()
    
    st.subheader("📈 Recent Sales History")
    if selected_customer:
        history_df = get_sales_history(selected_customer)
        if len(history_df) > 0:
            st.dataframe(history_df, use_container_width=True, hide_index=True)
            csv = history_df.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, f"{selected_customer}_history.csv", "text/csv")


def segment_head_page():
    st.title("Segment Head Intelligence Dashboard")
    st.markdown(f"Welcome, **{st.session_state.user_name}** | Your complete segment analysis hub")
    
    # Custom CSS for enhanced styling
    st.markdown("""
    <style>
        .dashboard-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            border-radius: 12px;
            color: white;
            margin-bottom: 20px;
        }
        .product-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
            margin: 10px 0;
        }
        .designation-stat {
            background: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            margin: 10px 0;
        }
        .trend-positive {
            color: #10b981;
            font-weight: bold;
        }
        .trend-negative {
            color: #ef4444;
            font-weight: bold;
        }
        .market-intel-card {
            background: linear-gradient(135deg, #fecba6 0%, #fd8d56 100%);
            padding: 15px;
            border-radius: 10px;
            color: #2d3748;
            margin: 10px 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Enhanced KPI dashboard
    stats = get_forecast_statistics()
    all_history = get_sales_history()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(" Total Volume", f"{stats['total_volume']:,.0f}", "units")
    with col2:
        st.metric(" Customers", stats["unique_customers"], "accounts")
    with col3:
        st.metric(" Forecasts", stats["total_forecasts"], "records")
    with col4:
        avg_monthly = all_history['volume'].mean() if len(all_history) > 0 else 0
        st.metric(" Avg Monthly", f"{avg_monthly:,.0f}", "units")
    with col5:
        st.metric(" Coverage", "100%", "active")
    
    st.divider()
    
    # Create tabs for organized dashboard
    tab1, tab2, tab3 = st.tabs([" Product Trends", " Designation Analysis", " Market Intelligence"])
    
    # TAB 1: Product Trends Per Designation
    with tab1:
        st.subheader("Per-Product & Per-Designation Trend Analysis")
        
        col1, col2 = st.columns([2, 2])
        
        with col1:
            # Get all designations
            all_designations = get_all_designations()
            selected_designations = st.multiselect(
                "Select Bearing Designations",
                all_designations,
                default=all_designations,
                key="sh_designations"
            )
        
        with col2:
            customers = get_all_customers()
            selected_customers = st.multiselect(
                "Filter by Customers",
                customers,
                default=customers,
                key="sh_customers"
            )
        
        if selected_designations and selected_customers:
            # Get filtered data
            filtered_df = get_filtered_sales_data(selected_customers, selected_designations)
            
            if len(filtered_df) > 0:
                # Trend per product (designation)
                st.subheader(" Trend by Bearing Designation")
                
                for designation in selected_designations:
                    des_data = filtered_df[filtered_df['designation'] == designation].sort_values('month')
                    if len(des_data) > 0:
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.line_chart(des_data.set_index('month')['volume'], use_container_width=True)
                        
                        with col2:
                            avg_vol = des_data['volume'].mean()
                            max_vol = des_data['volume'].max()
                            min_vol = des_data['volume'].min()
                            trend_pct = ((des_data.iloc[-1]['volume'] - des_data.iloc[0]['volume']) / des_data.iloc[0]['volume'] * 100) if len(des_data) > 1 else 0
                            
                            st.metric(f"{designation}", f"{avg_vol:.0f}", f"Trend: {trend_pct:+.1f}%")
                        
                        st.caption(f"Range: {min_vol:.0f} - {max_vol:.0f} units | Months: {len(des_data)}")
                        st.divider()
                
                # Monthly volume breakdown by designation
                st.subheader(" Monthly Volume Heatmap by Designation")
                pivot_data = filtered_df.pivot_table(
                    values='volume',
                    index='designation',
                    columns='month',
                    aggfunc='sum'
                )
                st.dataframe(pivot_data, use_container_width=True)
            else:
                st.warning("⚠️ No data available for selected filters")
    
    # TAB 2: Per-Designation Analysis
    with tab2:
        st.subheader("Volume Analysis by Designation & Month")
        
        col1, col2 = st.columns(2)
        
        with col1:
            all_designations = get_all_designations()
            selected_des_analysis = st.selectbox(
                "Select Designation for Detailed Analysis",
                all_designations,
                key="sh_des_select"
            )
        
        with col2:
            customers = get_all_customers()
            selected_cust_filter = st.multiselect(
                "Filter Customers",
                customers,
                default=customers,
                key="sh_cust_filter"
            )
        
        if selected_des_analysis and selected_cust_filter:
            des_history = get_filtered_sales_data(selected_cust_filter, [selected_des_analysis])
            
            if len(des_history) > 0:
                # Sort by month
                des_history['month'] = pd.to_datetime(des_history['month'])
                des_history = des_history.sort_values('month')
                des_history['month'] = des_history['month'].dt.strftime('%Y-%m')
                
                # Monthly stats
                monthly_stats = des_history.groupby('month').agg({
                    'volume': ['sum', 'mean', 'min', 'max', 'count']
                }).round(0)
                
                monthly_stats.columns = ['Total Volume', 'Avg per Customer', 'Min', 'Max', 'Customer Count']
                st.subheader(f" {selected_des_analysis} - Monthly Statistics")
                st.dataframe(monthly_stats, use_container_width=True)
                
                # Growth metrics
                col1, col2, col3 = st.columns(3)
                
                first_month_vol = des_history.groupby('month')['volume'].sum().iloc[0]
                last_month_vol = des_history.groupby('month')['volume'].sum().iloc[-1]
                growth = ((last_month_vol - first_month_vol) / first_month_vol * 100)
                
                with col1:
                    st.metric(" Growth Trend", f"{growth:+.1f}%", "Overall")
                
                with col2:
                    st.metric(" Avg Monthly Volume", f"{des_history['volume'].mean():,.0f}", "units")
                
                with col3:
                    st.metric(" Peak Month Volume", f"{des_history['volume'].max():,.0f}", "units")
                
                # Customer breakdown for this designation
                st.subheader(f"{selected_des_analysis} - Per Customer Analysis")
                
                customer_breakdown = des_history.groupby('customer_name').agg({
                    'volume': ['sum', 'mean', 'count']
                }).round(0)
                
                customer_breakdown.columns = ['Total Volume', 'Avg Monthly', 'Months']
                customer_breakdown = customer_breakdown.sort_values('Total Volume', ascending=False)
                
                st.dataframe(customer_breakdown, use_container_width=True)
                
                # Bar chart comparison
                st.bar_chart(des_history.groupby('month')['volume'].sum())
            else:
                st.warning("⚠️ No data available")
    
    # TAB 3: Market Intelligence
    with tab3:
        st.subheader("💡 Live Market Intelligence & Insights")
        
        customers = get_all_customers()
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_customer = st.selectbox("Select Customer for Intelligence", customers, key="sh_intel_customer")
        
        with col2:
            if st.button(" Generate Market Insights", use_container_width=True):
                st.session_state.gen_intel = True
        
        if selected_customer:
            customer_info = get_customer_info(selected_customer)
            
            # Customer info cards
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"<div class='designation-stat'><b>Company</b><br>{selected_customer}</div>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<div class='designation-stat'><b>Industry</b><br>{customer_info['industry']}</div>", unsafe_allow_html=True)
            with col3:
                st.markdown(f"<div class='designation-stat'><b>Region</b><br>{customer_info['region']}</div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='designation-stat'><b>Status</b><br> Active</div>", unsafe_allow_html=True)
            
            st.divider()
            
            # Market intelligence
            intel_df = get_customer_market_intelligence(selected_customer)
            
            if st.session_state.get('gen_intel', False) or len(intel_df) == 0:
                if st.button("Generate AI Market Intelligence", use_container_width=True, key="gen_intel_sh_btn"):
                    with st.spinner("🔍 Analyzing market landscape and competitors..."):
                        result = generate_market_intelligence(
                            selected_customer,
                            customer_info["industry"],
                            customer_info["region"]
                        )
                        if result["success"]:
                            source = result.get("source", "AI-Generated")
                            for ins in result["insights"]:
                                ins.setdefault("source", source)
                            save_market_intelligence(selected_customer, result["insights"])
                            st.success("✅ Market insights generated successfully!")
                            st.session_state.gen_intel = False
                            st.rerun()
                        else:
                            st.error(f"⚠️ Failed to generate insights: {result.get('error', 'Unknown error')}")
            
            if len(intel_df) > 0:
                st.subheader("📰 Latest Market Intelligence")
                for idx, (_, row) in enumerate(intel_df.iterrows()):
                    with st.container():
                        col1, col2 = st.columns([4, 1])
                        
                        with col1:
                            st.markdown(f"""
                            <div class='market-intel-card'>
                            <b>📌 {row['headline']}</b><br>
                            <small>Source: {row['source']} | Date: {row['created_at'][:10]}</small>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        with col2:
                            growth_color = "trend-positive" if row['growth_pct'] > 0 else "trend-negative"
                            st.markdown(f"<p class='{growth_color}'>Growth: {row['growth_pct']:+.0f}%</p>", unsafe_allow_html=True)
            else:
                st.info("💡 Click the button above to generate AI-powered market insights for this customer")
            
            st.divider()
            
            # Customer's performance summary
            st.subheader(f"📈 {selected_customer} - Performance Summary")
            
            cust_history = get_sales_history(selected_customer)
            if len(cust_history) > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Volume", f"{cust_history['volume'].sum():,.0f}")
                with col2:
                    st.metric("Avg Monthly", f"{cust_history['volume'].mean():,.0f}")
                with col3:
                    st.metric("Peak Volume", f"{cust_history['volume'].max():,.0f}")
                with col4:
                    months = len(cust_history['month'].unique())
                    st.metric("Months Tracked", months)
                
                st.line_chart(cust_history.sort_values('month').groupby('month')['volume'].sum())


def factory_head_page():
    st.title(" Factory Operations Dashboard")
    st.markdown(f"Welcome, **{st.session_state.user_name}** | Factory: **Pune** | Production & Inventory Management")
    
    # Enhanced styling
    st.markdown("""
    <style>
        .factory-stat {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 15px;
            border-radius: 10px;
            color: white;
        }
    </style>
    """, unsafe_allow_html=True)
    
    stats = get_forecast_statistics()
    col1, col2, col3 = st.columns(3)
    col1.metric(" Production Volume", f"{stats['total_volume']:,.0f}")
    col2.metric(" Customers", stats["unique_customers"])
    col3.metric(" Forecasts", stats["total_forecasts"])
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(" Production Data")
    
    with col2:
        view_option = st.radio("View By", ["All Customers", "Single Customer"], horizontal=True, key="fh_view")
    
    st.divider()
    
    all_history = get_sales_history()
    
    if view_option == "Single Customer":
        customers = get_all_customers()
        selected_cust = st.selectbox("Select Customer", customers, key="fh_customer")
        display_data = get_sales_history(selected_cust)
    else:
        display_data = all_history
    
    if len(display_data) > 0:
        st.dataframe(display_data, use_container_width=True, hide_index=True)
        
        st.divider()
        
        st.subheader("📈 Customer Performance Analysis")
        summary = display_data.groupby('customer_name').agg({
            'volume': ['sum', 'mean', 'count', 'min', 'max']
        }).round(0)
        
        summary.columns = ['Total Volume', 'Avg Monthly', 'Months', 'Min', 'Max']
        summary = summary.sort_values('Total Volume', ascending=False)
        st.dataframe(summary, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(" Volume Distribution by Customer")
            st.bar_chart(display_data.groupby('customer_name')['volume'].sum().sort_values(ascending=False))
        
        with col2:
            st.subheader(" Volume Trends Over Time")
            st.line_chart(display_data.groupby('month')['volume'].sum().sort_index())
        
        st.divider()
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            csv = display_data.to_csv(index=False)
            st.download_button("📥 Download CSV", csv, "production_data.csv", "text/csv", use_container_width=True)
        
        with col2:
            excel_buffer = io.BytesIO()
            with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
                display_data.to_excel(writer, index=False, sheet_name='Production')
                summary.to_excel(writer, sheet_name='Summary')
            excel_data = excel_buffer.getvalue()
            st.download_button("📊 Download Excel", excel_data, "production_data.xlsx", "application/vnd.ms-excel", use_container_width=True)


def main():
    init_db()
    
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        login_page()
    else:
        with st.sidebar:
            st.markdown("### Navigation")
            page = st.radio(
                "Select Dashboard",
                ["Dashboard", "Logout"],
                key="nav_radio"
            )
            
            if page == "Logout":
                st.session_state.authenticated = False
                st.session_state.clear()
                st.success("Logged out!")
                st.rerun()
            
            st.divider()
            st.caption(f"👤 {st.session_state.user_name}")
            st.caption(f"👨‍💼 {st.session_state.user_role.replace('_', ' ')}")
        
        if page == "Dashboard":
            if st.session_state.user_role == "ACCOUNT_MANAGER":
                account_manager_page()
            elif st.session_state.user_role == "SEGMENT_HEAD":
                segment_head_page()
            elif st.session_state.user_role == "FACTORY_HEAD":
                factory_head_page()


if __name__ == "__main__":
    main()
