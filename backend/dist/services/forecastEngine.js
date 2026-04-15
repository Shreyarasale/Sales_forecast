"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.generateForecast = generateForecast;
const axios_1 = __importDefault(require("axios"));
const pythonUrl = process.env.PYTHON_ENGINE_URL || "http://localhost:5001";
async function generateForecast(payload) {
    try {
        const response = await axios_1.default.post(`${pythonUrl}/forecast`, payload, { timeout: 5000 });
        return response.data;
    }
    catch {
        let multiplier = 1;
        if (payload.mode === "user_growth")
            multiplier = 1 + payload.growthPercent / 100;
        if (payload.mode === "market_intelligence")
            multiplier = 1 + payload.marketFactor / 100;
        if (payload.mode === "history")
            multiplier = 1.1;
        return {
            forecastVolume: Math.max(0, Math.round(payload.baseVolume * multiplier)),
            confidence: 0.8
        };
    }
}
