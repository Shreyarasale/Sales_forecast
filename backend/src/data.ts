import bcrypt from "bcryptjs";
import { AppUser, ForecastRecord } from "./types";

const hash = (value: string) => bcrypt.hashSync(value, 8);

export const users: AppUser[] = [
  {
    id: 1,
    username: "john.wicks",
    passwordHash: hash("password123"),
    role: "ACCOUNT_MANAGER",
    accountManagerId: 1
  },
  {
    id: 2,
    username: "rachel",
    passwordHash: hash("password123"),
    role: "SEGMENT_HEAD",
    segmentId: 101
  },
  {
    id: 3,
    username: "abhinav",
    passwordHash: hash("password123"),
    role: "FACTORY_HEAD",
    factoryId: 501
  }
];

export const accountManagerCustomers: Record<number, number[]> = {
  1: [1, 2]
};

export const customerNames: Record<number, string> = {
  1: "Mahindra Tractors",
  2: "Sonalika"
};

export const forecastStore: ForecastRecord[] = [
  {
    id: 1,
    customerId: 1,
    productDesignation: "6205-2RS",
    factory: "Pune",
    month: "2026-05",
    volume: 1000,
    finalVolume: 1100,
    generatedBy: "ACCOUNT_MANAGER",
    mode: "history",
    accountManagerId: 1
  },
  {
    id: 2,
    customerId: 2,
    productDesignation: "6206-ZZ",
    factory: "Pune",
    month: "2026-05",
    volume: 800,
    finalVolume: 860,
    generatedBy: "ACCOUNT_MANAGER",
    mode: "market_intelligence",
    accountManagerId: 1
  }
];

export const marketIntelligence = [
  {
    id: 1,
    title: "Tractor segment is projected to grow by 10% this quarter",
    customerIds: [1, 2],
    factor: 10
  },
  {
    id: 2,
    title: "Mahindra announced capex expansion in west India",
    customerIds: [1],
    factor: 6
  }
];
