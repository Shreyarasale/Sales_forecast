"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const exceljs_1 = __importDefault(require("exceljs"));
const data_1 = require("../data");
const auth_1 = require("../middleware/auth");
const router = (0, express_1.Router)();
const accountManagerNames = {
    1: "John Wicks"
};
const toProductLine = (designation) => designation.split("-")[0] || designation;
const toSegmentRows = () => data_1.forecastStore.map((row) => ({
    accountManager: accountManagerNames[row.accountManagerId] || `AM ${row.accountManagerId}`,
    customer: data_1.customerNames[row.customerId] || `Customer ${row.customerId}`,
    designation: row.productDesignation,
    productLine: toProductLine(row.productDesignation),
    factory: row.factory,
    month: row.month,
    forecastVolume: row.finalVolume
}));
const parseTeamMembers = (value) => {
    if (!value) {
        return [];
    }
    return value
        .split(",")
        .map((item) => item.trim())
        .filter(Boolean);
};
const filterSegmentRows = (rows, filters) => {
    const teamMemberSet = new Set(filters.teamMembers || []);
    return rows.filter((row) => {
        return ((!filters.customer || row.customer.includes(filters.customer)) &&
            (!filters.designation || row.designation.includes(filters.designation)) &&
            (!filters.factory || row.factory.includes(filters.factory)) &&
            (!filters.month || row.month.includes(filters.month)) &&
            (!teamMemberSet.size || teamMemberSet.has(row.accountManager)));
    });
};
router.get("/forecasts.csv", auth_1.authenticate, (_req, res) => {
    const header = ["id", "customerId", "designation", "factory", "month", "baseVolume", "finalVolume", "mode"];
    const lines = data_1.forecastStore.map((f) => [f.id, f.customerId, f.productDesignation, f.factory, f.month, f.volume, f.finalVolume, f.mode].join(","));
    const csv = [header.join(","), ...lines].join("\n");
    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", "attachment; filename=forecast-export.csv");
    return res.send(csv);
});
router.get("/forecasts.xlsx", auth_1.authenticate, async (_req, res) => {
    const workbook = new exceljs_1.default.Workbook();
    const sheet = workbook.addWorksheet("Forecasts");
    sheet.columns = [
        { header: "ID", key: "id", width: 10 },
        { header: "Customer ID", key: "customerId", width: 15 },
        { header: "Designation", key: "productDesignation", width: 20 },
        { header: "Factory", key: "factory", width: 15 },
        { header: "Month", key: "month", width: 12 },
        { header: "Base Volume", key: "volume", width: 12 },
        { header: "Final Volume", key: "finalVolume", width: 12 },
        { header: "Mode", key: "mode", width: 20 }
    ];
    data_1.forecastStore.forEach((row) => sheet.addRow(row));
    res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    res.setHeader("Content-Disposition", "attachment; filename=forecast-export.xlsx");
    await workbook.xlsx.write(res);
    return res.end();
});
router.get("/segment-head.csv", auth_1.authenticate, (0, auth_1.authorize)(["SEGMENT_HEAD"]), (req, res) => {
    const customer = String(req.query.customer || "");
    const designation = String(req.query.designation || "");
    const factory = String(req.query.factory || "");
    const month = String(req.query.month || "");
    const teamMembers = parseTeamMembers(String(req.query.teamMembers || ""));
    const rows = filterSegmentRows(toSegmentRows(), {
        customer,
        designation,
        factory,
        month,
        teamMembers
    });
    const header = [
        "accountManager",
        "customer",
        "designation",
        "productLine",
        "factory",
        "month",
        "forecastVolume"
    ];
    const lines = rows.map((row) => [
        row.accountManager,
        row.customer,
        row.designation,
        row.productLine,
        row.factory,
        row.month,
        row.forecastVolume
    ].join(","));
    const csv = [header.join(","), ...lines].join("\n");
    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", "attachment; filename=segment-head-export.csv");
    return res.send(csv);
});
router.get("/segment-head.xlsx", auth_1.authenticate, (0, auth_1.authorize)(["SEGMENT_HEAD"]), async (req, res) => {
    const customer = String(req.query.customer || "");
    const designation = String(req.query.designation || "");
    const factory = String(req.query.factory || "");
    const month = String(req.query.month || "");
    const teamMembers = parseTeamMembers(String(req.query.teamMembers || ""));
    const rows = filterSegmentRows(toSegmentRows(), {
        customer,
        designation,
        factory,
        month,
        teamMembers
    });
    const workbook = new exceljs_1.default.Workbook();
    const sheet = workbook.addWorksheet("Segment Head View");
    sheet.columns = [
        { header: "Account Manager", key: "accountManager", width: 20 },
        { header: "Customer", key: "customer", width: 24 },
        { header: "Designation", key: "designation", width: 18 },
        { header: "Product Line", key: "productLine", width: 16 },
        { header: "Factory", key: "factory", width: 12 },
        { header: "Month", key: "month", width: 12 },
        { header: "Forecast Volume", key: "forecastVolume", width: 16 }
    ];
    rows.forEach((row) => sheet.addRow(row));
    res.setHeader("Content-Type", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
    res.setHeader("Content-Disposition", "attachment; filename=segment-head-export.xlsx");
    await workbook.xlsx.write(res);
    return res.end();
});
exports.default = router;
