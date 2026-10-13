import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { dashboardSummary } from "../api/tickets.js";

const CARDS = [
  ["open", "Open"],
  ["in_progress", "In Progress"],
  ["waiting", "Waiting"],
  ["resolved", "Resolved"],
  ["closed", "Closed"],
];

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    dashboardSummary().then(setSummary).catch((e) => setError(e.message));
  }, []);

  return (
    <div>
      <h1>Dashboard</h1>
      {error && <div className="alert alert-error">{error}</div>}
      <div className="stat-grid">
        {CARDS.map(([key, label]) => (
          <div className="card stat" key={key}>
            <span className="stat-value">{summary ? summary[key] : "–"}</span>
            <span className="stat-label">{label}</span>
          </div>
        ))}
      </div>
      <p className="muted">
        Total tickets: {summary ? summary.total : "–"} · <Link to="/tickets">View all tickets</Link>
      </p>
    </div>
  );
}
