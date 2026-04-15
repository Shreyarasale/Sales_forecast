import { Router } from "express";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import { users } from "../data";

const router = Router();
const jwtSecret = process.env.JWT_SECRET || "demo-secret";

router.post("/login", async (req, res) => {
  const { username, password } = req.body as { username: string; password: string };
  const user = users.find((u) => u.username === username);

  if (!user || !(await bcrypt.compare(password, user.passwordHash))) {
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

  const token = jwt.sign(payload, jwtSecret, { expiresIn: "8h" });
  return res.json({ token, user: payload });
});

export default router;
