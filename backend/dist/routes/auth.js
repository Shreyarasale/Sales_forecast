"use strict";
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const express_1 = require("express");
const bcryptjs_1 = __importDefault(require("bcryptjs"));
const jsonwebtoken_1 = __importDefault(require("jsonwebtoken"));
const data_1 = require("../data");
const router = (0, express_1.Router)();
const jwtSecret = process.env.JWT_SECRET || "demo-secret";
router.post("/login", async (req, res) => {
    const { username, password } = req.body;
    const user = data_1.users.find((u) => u.username === username);
    if (!user || !(await bcryptjs_1.default.compare(password, user.passwordHash))) {
        return res.status(401).json({ message: "Invalid credentials" });
    }
    const payload = {
        id: user.id,
        username: user.username,
        role: user.role,
        segmentId: user.segmentId,
        factoryId: user.factoryId,
        accountManagerId: user.accountManagerId
    };
    const token = jsonwebtoken_1.default.sign(payload, jwtSecret, { expiresIn: "8h" });
    return res.json({ token, user: payload });
});
exports.default = router;
