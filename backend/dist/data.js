"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.marketIntelligence = exports.forecastStore = exports.customerNames = exports.accountManagerCustomers = exports.users = void 0;
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const hash = (value) => bcryptjs_1.default.hashSync(value, 8);
exports.users = [
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
exports.accountManagerCustomers = {
    1: [1, 2]
};
exports.customerNames = {
    1: "Mahindra Tractors",
    2: "Sonalika"
};
exports.forecastStore = [
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
exports.marketIntelligence = [
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
