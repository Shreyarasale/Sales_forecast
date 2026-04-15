export type Role = "ACCOUNT_MANAGER" | "SEGMENT_HEAD" | "FACTORY_HEAD";

export type AppUser = {
  id: number;
  username: string;
  passwordHash: string;
  role: Role;
  segmentId?: number;
  factoryId?: number;
  accountManagerId?: number;
};

export type ForecastInput = {
  customerId: number;
  productDesignation: string;
  factory: string;
  month: string;
  volume: number;
};

export type ForecastRecord = ForecastInput & {
  id: number;
  accountManagerId: number;
  generatedBy: Role;
  mode: "history" | "user_growth" | "market_intelligence";
  finalVolume: number;
};
