import { Router } from "express";
import { customerNames, forecastStore } from "../data";
import { authenticate, authorize } from "../middleware/auth";

const router = Router();

router.get(
  "/account-manager",
  authenticate,
  authorize(["ACCOUNT_MANAGER"]),
  (req, res) => {
    const managerId = req.user!.accountManagerId || 0;
    const rows = forecastStore.filter((item) => item.accountManagerId === managerId);
    const customerMonthly = rows.map((row) => ({
      customer: customerNames[row.customerId] || `Customer ${row.customerId}`,
      month: row.month,
      forecastVolume: row.finalVolume
    }));
    return res.json({ customerMonthly });
  }
);

router.get(
  "/segment-head",
  authenticate,
  authorize(["SEGMENT_HEAD"]),
  (_req, res) => {
    const rows = forecastStore.map((row) => ({
      accountManager: "John Wicks",
      customer: customerNames[row.customerId] || `Customer ${row.customerId}`,
      designation: row.productDesignation,
      factory: row.factory,
      month: row.month,
      forecastVolume: row.finalVolume
    }));
    return res.json({ rows });
  }
);

router.get(
  "/factory-head",
  authenticate,
  authorize(["FACTORY_HEAD"]),
  (_req, res) => {
    const rows = forecastStore
      .filter((row) => row.factory === "Pune")
      .map((row) => ({
        factory: row.factory,
        month: row.month,
        designation: row.productDesignation,
        forecastVolume: row.finalVolume
      }));
    return res.json({ rows });
  }
);

export default router;
