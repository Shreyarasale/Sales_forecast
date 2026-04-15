import { Router } from "express";
import { accountManagerCustomers, marketIntelligence } from "../data";
import { authenticate } from "../middleware/auth";

const router = Router();

router.get("/", authenticate, (req, res) => {
  if (!req.user) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  if (req.user.role === "ACCOUNT_MANAGER") {
    const customerIds = accountManagerCustomers[req.user.accountManagerId || 0] || [];
    const items = marketIntelligence.filter((m) => m.customerIds.some((id) => customerIds.includes(id)));
    return res.json({ items });
  }

  return res.json({ items: marketIntelligence });
});

export default router;
