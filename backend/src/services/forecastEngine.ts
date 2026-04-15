import axios from "axios";

const pythonUrl = process.env.PYTHON_ENGINE_URL || "http://localhost:5001";

type GeneratePayload = {
  mode: "history" | "user_growth" | "market_intelligence";
  growthPercent: number;
  baseVolume: number;
  marketFactor: number;
};

export async function generateForecast(payload: GeneratePayload) {
  try {
    const response = await axios.post(`${pythonUrl}/forecast`, payload, { timeout: 5000 });
    return response.data as { forecastVolume: number; confidence: number };
  } catch {
    let multiplier = 1;
    if (payload.mode === "user_growth") multiplier = 1 + payload.growthPercent / 100;
    if (payload.mode === "market_intelligence") multiplier = 1 + payload.marketFactor / 100;
    if (payload.mode === "history") multiplier = 1.1;
    return {
      forecastVolume: Math.max(0, Math.round(payload.baseVolume * multiplier)),
      confidence: 0.8
    };
  }
}
