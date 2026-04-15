"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const data_1 = require("../data");
const auth_1 = require("../middleware/auth");
const router = (0, express_1.Router)();
const accountManagerNames = {
    1: "John Wicks"
};
const toProductLine = (designation) => designation.split("-")[0] || designation;
router.get("/account-manager", auth_1.authenticate, (0, auth_1.authorize)(["ACCOUNT_MANAGER"]), (req, res) => {
    const managerId = req.user.accountManagerId || 0;
    const rows = data_1.forecastStore.filter((item) => item.accountManagerId === managerId);
    const customerMonthly = rows.map((row) => ({
        customer: data_1.customerNames[row.customerId] || `Customer ${row.customerId}`,
        month: row.month,
        forecastVolume: row.finalVolume
    }));
    return res.json({ customerMonthly });
});
router.get("/segment-head", auth_1.authenticate, (0, auth_1.authorize)(["SEGMENT_HEAD"]), (_req, res) => {
    const rows = data_1.forecastStore.map((row) => ({
        accountManager: accountManagerNames[row.accountManagerId] || `AM ${row.accountManagerId}`,
        customer: data_1.customerNames[row.customerId] || `Customer ${row.customerId}`,
        designation: row.productDesignation,
        productLine: toProductLine(row.productDesignation),
        factory: row.factory,
        month: row.month,
        forecastVolume: row.finalVolume
    }));
    const teamMembers = Array.from(new Set(rows.map((row) => row.accountManager))).sort();
    const designationMonthlyVolumeMap = new Map();
    const productLineMonthlyTrendMap = new Map();
    rows.forEach((row) => {
        const designationKey = `${row.month}||${row.designation}`;
        designationMonthlyVolumeMap.set(designationKey, (designationMonthlyVolumeMap.get(designationKey) || 0) + row.forecastVolume);
        const productLineKey = `${row.month}||${row.productLine}`;
        productLineMonthlyTrendMap.set(productLineKey, (productLineMonthlyTrendMap.get(productLineKey) || 0) + row.forecastVolume);
    });
    const designationMonthlyVolume = Array.from(designationMonthlyVolumeMap.entries())
        .map(([key, totalVolume]) => {
        const [month, designation] = key.split("||");
        return { month, designation, totalVolume };
    })
        .sort((a, b) => a.month.localeCompare(b.month) || a.designation.localeCompare(b.designation));
    const productLineMonthlyTrend = Array.from(productLineMonthlyTrendMap.entries())
        .map(([key, totalVolume]) => {
        const [month, productLine] = key.split("||");
        return { month, productLine, totalVolume };
    })
        .sort((a, b) => a.month.localeCompare(b.month) || a.productLine.localeCompare(b.productLine));
    const liveMarketIntelligence = data_1.marketIntelligence.map((item) => {
        const impactedCustomers = item.customerIds
            .map((id) => data_1.customerNames[id] || `Customer ${id}`)
            .join(", ");
        return {
            id: item.id,
            title: item.title,
            impactPercent: item.factor,
            impactedCustomers,
            observedAt: new Date().toISOString()
        };
    });
    return res.json({
        rows,
        teamMembers,
        designationMonthlyVolume,
        productLineMonthlyTrend,
        liveMarketIntelligence
    });
});
router.get("/factory-head", auth_1.authenticate, (0, auth_1.authorize)(["FACTORY_HEAD"]), (_req, res) => {
    const rows = data_1.forecastStore
        .filter((row) => row.factory === "Pune")
        .map((row) => ({
        factory: row.factory,
        month: row.month,
        designation: row.productDesignation,
        forecastVolume: row.finalVolume
    }));
    return res.json({ rows });
});
exports.default = router;
