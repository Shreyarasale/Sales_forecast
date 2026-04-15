import { Router } from "express";
import ExcelJS from "exceljs";
import { customerNames, forecastStore } from "../data";
import { authenticate, authorize } from "../middleware/auth";

const router = Router();

const accountManagerNames: Record<number, string> = {
  1: "John Wicks"
};

type SegmentExportRow = {
  accountManager: string;
  customer: string;
  designation: string;
  productLine: string;
  factory: string;
  month: string;
  forecastVolume: number;
};

const toProductLine = (designation: string) => designation.split("-")[0] || designation;

const toSegmentRows = (): SegmentExportRow[] =>
  forecastStore.map((row) => ({
    accountManager: accountManagerNames[row.accountManagerId] || `AM ${row.accountManagerId}`,
    customer: customerNames[row.customerId] || `Customer ${row.customerId}`,
    designation: row.productDesignation,
    productLine: toProductLine(row.productDesignation),
    factory: row.factory,
    month: row.month,
    forecastVolume: row.finalVolume
  }));

const parseTeamMembers = (value: string | undefined): string[] => {
  if (!value) {
    return [];
  }
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
};

const filterSegmentRows = (
  rows: SegmentExportRow[],
  filters: {
    customer?: string;
    designation?: string;
    factory?: string;
    month?: string;
    teamMembers?: string[];
  }
) => {
  const teamMemberSet = new Set(filters.teamMembers || []);
  return rows.filter((row) => {
    return (
      (!filters.customer || row.customer.includes(filters.customer)) &&
      (!filters.designation || row.designation.includes(filters.designation)) &&
      (!filters.factory || row.factory.includes(filters.factory)) &&
      (!filters.month || row.month.includes(filters.month)) &&
      (!teamMemberSet.size || teamMemberSet.has(row.accountManager))
    );
  });
};

router.get("/forecasts.csv", authenticate, (_req, res) => {
  const header = ["id", "customerId", "designation", "factory", "month", "baseVolume", "finalVolume", "mode"];
  const lines = forecastStore.map((f) =>
    [f.id, f.customerId, f.productDesignation, f.factory, f.month, f.volume, f.finalVolume, f.mode].join(",")
  );
  const csv = [header.join(","), ...lines].join("\n");

  res.setHeader("Content-Type", "text/csv");
  res.setHeader("Content-Disposition", "attachment; filename=forecast-export.csv");
  return res.send(csv);
});

router.get("/forecasts.xlsx", authenticate, async (_req, res) => {
  const workbook = new ExcelJS.Workbook();
  const sheet = workbook.addWorksheet("Forecasts");
  sheet.columns = [
    { header: "ID", key: "id", width: 10 },
    { header: "Customer ID", key: "customerId", width: 15 },
    { header: "Designation", key: "productDesignation", width: 20 },
    { header: "Factory", key: "factory", width: 15 },
    { header: "Month", key: "month", width: 12 },
    { header: "Base Volume", key: "volume", width: 12 },
    { header: "Final Volume", key: "finalVolume", width: 12 },
    { header: "Mode", key: "mode", width: 20 }
  ];

  forecastStore.forEach((row) => sheet.addRow(row));

  res.setHeader(
    "Content-Type",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
  );
  res.setHeader("Content-Disposition", "attachment; filename=forecast-export.xlsx");

  await workbook.xlsx.write(res);
  return res.end();
});

router.get(
  "/segment-head.csv",
  authenticate,
  authorize(["SEGMENT_HEAD"]),
  (req, res) => {
    const customer = String(req.query.customer || "");
    const designation = String(req.query.designation || "");
    const factory = String(req.query.factory || "");
    const month = String(req.query.month || "");
    const teamMembers = parseTeamMembers(String(req.query.teamMembers || ""));

    const rows = filterSegmentRows(toSegmentRows(), {
      customer,
      designation,
      factory,
      month,
      teamMembers
    });

    const header = [
      "accountManager",
      "customer",
      "designation",
      "productLine",
      "factory",
      "month",
      "forecastVolume"
    ];
    const lines = rows.map((row) =>
      [
        row.accountManager,
        row.customer,
        row.designation,
        row.productLine,
        row.factory,
        row.month,
        row.forecastVolume
      ].join(",")
    );

    const csv = [header.join(","), ...lines].join("\n");

    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", "attachment; filename=segment-head-export.csv");
    return res.send(csv);
  }
);

router.get(
  "/segment-head.xlsx",
  authenticate,
  authorize(["SEGMENT_HEAD"]),
  async (req, res) => {
    const customer = String(req.query.customer || "");
    const designation = String(req.query.designation || "");
    const factory = String(req.query.factory || "");
    const month = String(req.query.month || "");
    const teamMembers = parseTeamMembers(String(req.query.teamMembers || ""));

    const rows = filterSegmentRows(toSegmentRows(), {
      customer,
      designation,
      factory,
      month,
      teamMembers
    });

    const workbook = new ExcelJS.Workbook();
    const sheet = workbook.addWorksheet("Segment Head View");
    sheet.columns = [
      { header: "Account Manager", key: "accountManager", width: 20 },
      { header: "Customer", key: "customer", width: 24 },
      { header: "Designation", key: "designation", width: 18 },
      { header: "Product Line", key: "productLine", width: 16 },
      { header: "Factory", key: "factory", width: 12 },
      { header: "Month", key: "month", width: 12 },
      { header: "Forecast Volume", key: "forecastVolume", width: 16 }
    ];

    rows.forEach((row) => sheet.addRow(row));

    res.setHeader(
      "Content-Type",
      "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    );
    res.setHeader("Content-Disposition", "attachment; filename=segment-head-export.xlsx");

    await workbook.xlsx.write(res);
    return res.end();
  }
);

export default router;
