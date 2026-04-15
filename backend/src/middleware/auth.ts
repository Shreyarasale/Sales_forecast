import { NextFunction, Request, Response } from "express";
import jwt from "jsonwebtoken";
import { AppUser, Role } from "../types";

declare module "express-serve-static-core" {
  interface Request {
    user?: Omit<AppUser, "passwordHash">;
  }
}

const jwtSecret = process.env.JWT_SECRET || "demo-secret";

export function authenticate(req: Request, res: Response, next: NextFunction) {
  const authHeader = req.headers.authorization;
  if (!authHeader?.startsWith("Bearer ")) {
    return res.status(401).json({ message: "Unauthorized" });
  }

  const token = authHeader.slice(7);

  try {
    const payload = jwt.verify(token, jwtSecret) as Omit<AppUser, "passwordHash">;
    req.user = payload;
    return next();
  } catch {
    return res.status(401).json({ message: "Invalid token" });
  }
}

export function authorize(allowedRoles: Role[]) {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user || !allowedRoles.includes(req.user.role)) {
      return res.status(403).json({ message: "Forbidden" });
    }
    return next();
  };
}
