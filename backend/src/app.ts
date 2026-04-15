import express from "express";
import cors from "cors";
import helmet from "helmet";
import authRoutes from "./routes/auth";
import forecastRoutes from "./routes/forecasts";
import dashboardRoutes from "./routes/dashboards";
import exportRoutes from "./routes/exports";
import marketRoutes from "./routes/market";

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.get("/health", (_req, res) => res.json({ status: "ok" }));

app.use("/api/auth", authRoutes);
app.use("/api/forecasts", forecastRoutes);
app.use("/api/dashboards", dashboardRoutes);
app.use("/api/exports", exportRoutes);
app.use("/api/market-intelligence", marketRoutes);

export default app;
