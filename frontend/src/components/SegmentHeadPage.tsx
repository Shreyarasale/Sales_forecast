import { useEffect, useState } from "react";
import { api } from "../api";

type SegmentRow = {
  accountManager: string;
  customer: string;
  designation: string;
  factory: string;
  month: string;
  forecastVolume: number;
};

export default function SegmentHeadPage() {
  const [rows, setRows] = useState<SegmentRow[]>([]);
  const [filter, setFilter] = useState({
    accountManager: "",
    customer: "",
    designation: "",
    factory: "",
    month: ""
  });

  useEffect(() => {
    api.get("/dashboards/segment-head").then((res) => setRows(res.data.rows));
  }, []);

  const filtered = rows.filter((row) => {
    return (
      (!filter.accountManager || row.accountManager.includes(filter.accountManager)) &&
      (!filter.customer || row.customer.includes(filter.customer)) &&
      (!filter.designation || row.designation.includes(filter.designation)) &&
      (!filter.factory || row.factory.includes(filter.factory)) &&
      (!filter.month || row.month.includes(filter.month))
    );
  });

  const total = filtered.reduce((sum, r) => sum + r.forecastVolume, 0);

  return (
    <div className="stack">
      <section className="card">
        <h2>Rachel - Segment Head Dashboard</h2>
        <div className="grid-5">
          <input
            placeholder="Filter AM"
            value={filter.accountManager}
            onChange={(e) => setFilter({ ...filter, accountManager: e.target.value })}
          />
          <input
            placeholder="Filter Customer"
            value={filter.customer}
            onChange={(e) => setFilter({ ...filter, customer: e.target.value })}
          />
          <input
            placeholder="Filter Designation"
            value={filter.designation}
            onChange={(e) => setFilter({ ...filter, designation: e.target.value })}
          />
          <input
            placeholder="Filter Factory"
            value={filter.factory}
            onChange={(e) => setFilter({ ...filter, factory: e.target.value })}
          />
          <input
            placeholder="Filter Month"
            value={filter.month}
            onChange={(e) => setFilter({ ...filter, month: e.target.value })}
          />
        </div>
      </section>

      <section className="card row-between">
        <div>
          <strong>Filtered Rows:</strong> {filtered.length}
        </div>
        <div>
          <strong>Total Forecast:</strong> {total}
        </div>
      </section>

      <section className="card">
        <table>
          <thead>
            <tr>
              <th>Account Manager</th>
              <th>Customer</th>
              <th>Designation</th>
              <th>Factory</th>
              <th>Month</th>
              <th>Forecast Volume</th>
            </tr>
          </thead>
          <tbody>
            {filtered.map((row, index) => (
              <tr key={index}>
                <td>{row.accountManager}</td>
                <td>{row.customer}</td>
                <td>{row.designation}</td>
                <td>{row.factory}</td>
                <td>{row.month}</td>
                <td>{row.forecastVolume}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
