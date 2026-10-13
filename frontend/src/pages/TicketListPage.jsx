import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listTickets } from "../api/tickets.js";
import StatusBadge from "../components/StatusBadge.jsx";

const STATUSES = ["", "Open", "In Progress", "Waiting", "Resolved", "Closed"];
const PRIORITIES = ["", "Low", "Medium", "High", "Urgent"];

export default function TicketListPage() {
  const [tickets, setTickets] = useState([]);
  const [total, setTotal] = useState(0);
  const [filters, setFilters] = useState({ status: "", priority: "", search: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    listTickets(filters)
      .then((data) => {
        setTickets(data.items);
        setTotal(data.total);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [filters]);

  function update(key, value) {
    setFilters((prev) => ({ ...prev, [key]: value }));
  }

  return (
    <div>
      <div className="page-head">
        <h1>Tickets</h1>
        <Link className="btn btn-primary" to="/tickets/new">
          New ticket
        </Link>
      </div>

      <div className="card filters">
        <input
          placeholder="Search title or description"
          value={filters.search}
          onChange={(e) => update("search", e.target.value)}
        />
        <select value={filters.status} onChange={(e) => update("status", e.target.value)}>
          {STATUSES.map((s) => (
            <option key={s} value={s}>
              {s || "All statuses"}
            </option>
          ))}
        </select>
        <select value={filters.priority} onChange={(e) => update("priority", e.target.value)}>
          {PRIORITIES.map((p) => (
            <option key={p} value={p}>
              {p || "All priorities"}
            </option>
          ))}
        </select>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {loading ? (
        <p className="muted">Loading…</p>
      ) : tickets.length === 0 ? (
        <p className="muted">No tickets match these filters.</p>
      ) : (
        <table className="table card">
          <thead>
            <tr>
              <th>#</th>
              <th>Title</th>
              <th>Category</th>
              <th>Priority</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map((t) => (
              <tr key={t.id}>
                <td>{t.id}</td>
                <td>
                  <Link to={`/tickets/${t.id}`}>{t.title}</Link>
                </td>
                <td>{t.category}</td>
                <td>{t.priority}</td>
                <td>
                  <StatusBadge value={t.status} />
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
      <p className="muted">{total} ticket(s)</p>
    </div>
  );
}
