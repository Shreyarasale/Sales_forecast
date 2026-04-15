import { Router } from "express";
import { accountManagerCustomers, forecastStore, marketIntelligence } from "../data";
import { authenticate, authorize } from "../middleware/auth";
import { generateForecast } from "../services/forecastEngine";
import { ForecastInput, ForecastRecord } from "../types";

const router = Router();

router.post(
  "/generate",
  authenticate,
  authorize(["ACCOUNT_MANAGER"]),
  async (req, res) => {
    const { mode, growthPercent, inputs } = req.body as {
      mode: "history" | "user_growth" | "market_intelligence";
      growthPercent: number;
      inputs: ForecastInput[];
    };

    const user = req.user!;
    const managerId = user.accountManagerId || 0;
    const allowedCustomers = new Set(accountManagerCustomers[managerId] || []);

    const denied = inputs.some((input) => !allowedCustomers.has(input.customerId));
    if (denied) {
      return res.status(403).json({ message: "Cannot modify unassigned customer forecast lines" });
    }

    const generated: ForecastRecord[] = [];

    for (const input of inputs) {
      const marketFactor =
        marketIntelligence
          .filter((m) => m.customerIds.includes(input.customerId))
          .reduce((sum, item) => sum + item.factor, 0) || 0;

      const result = await generateForecast({
        mode,
        growthPercent,
        baseVolume: input.volume,
        marketFactor
      });

      const record: ForecastRecord = {
        id: forecastStore.length + generated.length + 1,
        ...input,
        accountManagerId: managerId,
        generatedBy: user.role,
        mode,
        finalVolume: result.forecastVolume
      };
      generated.push(record);
    }

    forecastStore.push(...generated);

    return res.json({
      message: "Forecast generated",
      generatedCount: generated.length,
      rows: generated
    });
  }
);

router.get("/", authenticate, (req, res) => {
  if (!req.user) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  if (req.user.role === "ACCOUNT_MANAGER") {
    const managerId = req.user.accountManagerId || 0;
    return res.json({ rows: forecastStore.filter((f) => f.accountManagerId === managerId) });
  }

  if (req.user.role === "SEGMENT_HEAD") {
    return res.json({ rows: forecastStore });
  }

  if (req.user.role === "FACTORY_HEAD") {
    return res.json({ rows: forecastStore.filter((f) => f.factory === "Pune") });
  }

  return res.json({ rows: [] });
});

export default router;
