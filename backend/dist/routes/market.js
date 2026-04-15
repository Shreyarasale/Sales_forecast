"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const data_1 = require("../data");
const auth_1 = require("../middleware/auth");
const router = (0, express_1.Router)();
router.get("/", auth_1.authenticate, (req, res) => {
    if (!req.user) {
        return res.status(401).json({ message: "Unauthorized" });
    }
    if (req.user.role === "ACCOUNT_MANAGER") {
        const customerIds = data_1.accountManagerCustomers[req.user.accountManagerId || 0] || [];
        const items = data_1.marketIntelligence.filter((m) => m.customerIds.some((id) => customerIds.includes(id)));
        return res.json({ items });
    }
    return res.json({ items: data_1.marketIntelligence });
});
exports.default = router;
