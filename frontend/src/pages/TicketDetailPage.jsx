import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { addComment, aiSuggest, getTicket, updateTicket } from "../api/tickets.js";
import { useAuth } from "../auth/AuthContext.jsx";
import StatusBadge from "../components/StatusBadge.jsx";

const PRIORITIES = ["Low", "Medium", "High", "Urgent"];
const STATUSES = ["Open", "In Progress", "Waiting", "Resolved", "Closed"];

export default function TicketDetailPage() {
  const { id } = useParams();
  const { isStaff } = useAuth();
  const [ticket, setTicket] = useState(null);
  const [error, setError] = useState("");
  const [comment, setComment] = useState("");
  const [suggestion, setSuggestion] = useState(null);

  function load() {
    getTicket(id).then(setTicket).catch((e) => setError(e.message));
  }

  useEffect(load, [id]);

  async function apply(patch) {
    setError("");
    try {
      await updateTicket(id, patch);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function submitComment(e) {
    e.preventDefault();
    if (!comment.trim()) return;
    try {
      await addComment(id, comment);
      setComment("");
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function askAi() {
    setError("");
    try {
      setSuggestion(await aiSuggest(id));
    } catch (e) {
      setError(e.message);
    }
  }

  if (error && !ticket) return <div className="alert alert-error">{error}</div>;
  if (!ticket) return <p className="muted">Loading…</p>;

  return (
    <div>
      <div className="page-head">
        <h1>
          #{ticket.id} {ticket.title}
        </h1>
        <StatusBadge value={ticket.status} />
      </div>
      {error && <div className="alert alert-error">{error}</div>}

      <div className="card">
        <p>{ticket.description}</p>
        <p className="muted">
          Category: {ticket.category} · Priority: {ticket.priority} · Requester: #{ticket.requester_id} · Assignee:{" "}
          {ticket.assignee_id ? `#${ticket.assignee_id}` : "unassigned"}
        </p>
      </div>

      {isStaff && (
        <div className="card row">
          <label>
            Status
            <select value={ticket.status} onChange={(e) => apply({ status: e.target.value })}>
              {STATUSES.map((s) => (
                <option key={s} value={s}>
                  {s}
                </option>
              ))}
            </select>
          </label>
          <label>
            Priority
            <select value={ticket.priority} onChange={(e) => apply({ priority: e.target.value })}>
              {PRIORITIES.map((p) => (
                <option key={p} value={p}>
                  {p}
                </option>
              ))}
            </select>
          </label>
          <button className="btn" onClick={askAi}>
            Suggest with AI
          </button>
        </div>
      )}

      {suggestion && (
        <div className="card ai-card">
          <h3>AI suggestion (review before applying)</h3>
          <p>
            Suggested category: <strong>{suggestion.category}</strong> · priority:{" "}
            <strong>{suggestion.priority}</strong>
          </p>
          <p className="muted">{suggestion.rationale}</p>
          <p className="muted">
            Provider: {suggestion.provider} / {suggestion.model}
          </p>
          <pre className="draft">{suggestion.draft_reply}</pre>
          <div className="row">
            <button className="btn" onClick={() => apply({ category: suggestion.category })}>
              Apply category
            </button>
            <button className="btn" onClick={() => apply({ priority: suggestion.priority })}>
              Apply priority
            </button>
            <button className="btn btn-ghost" onClick={() => setComment(suggestion.draft_reply)}>
              Copy draft to comment
            </button>
          </div>
        </div>
      )}

      <h2>Comments</h2>
      <form className="card form" onSubmit={submitComment}>
        <textarea
          rows={3}
          value={comment}
          onChange={(e) => setComment(e.target.value)}
          placeholder="Add a comment…"
        />
        <button className="btn btn-primary" type="submit">
          Post comment
        </button>
      </form>
      <ul className="comments">
        {ticket.comments.map((c) => (
          <li key={c.id} className="card">
            <p>{c.body}</p>
            <p className="muted">User #{c.author_id} · {new Date(c.created_at).toLocaleString()}</p>
          </li>
        ))}
      </ul>

      <h2>Activity</h2>
      <ul className="timeline">
        {ticket.events.map((ev) => (
          <li key={ev.id}>
            <span className="muted">{new Date(ev.created_at).toLocaleString()}</span> — <strong>{ev.event_type}</strong>
            {ev.detail ? `: ${ev.detail}` : ""}
          </li>
        ))}
      </ul>
    </div>
  );
}
