import { useState } from "react";

const PRIORITIES = ["Low", "Medium", "High", "Urgent"];
const CATEGORIES = ["general", "billing", "account", "technical", "bug", "other"];

export default function TicketForm({ onSubmit, submitting, error }) {
  const [form, setForm] = useState({ title: "", description: "", category: "general", priority: "Medium" });

  function update(key, value) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  function handleSubmit(e) {
    e.preventDefault();
    onSubmit(form);
  }

  return (
    <form className="card form" onSubmit={handleSubmit}>
      {error && <div className="alert alert-error">{error}</div>}
      <label>
        Title
        <input
          required
          minLength={3}
          maxLength={200}
          value={form.title}
          onChange={(e) => update("title", e.target.value)}
          placeholder="Short summary of the problem"
        />
      </label>
      <label>
        Description
        <textarea
          required
          minLength={3}
          rows={5}
          value={form.description}
          onChange={(e) => update("description", e.target.value)}
          placeholder="What happened? What did you expect?"
        />
      </label>
      <div className="row">
        <label>
          Category
          <select value={form.category} onChange={(e) => update("category", e.target.value)}>
            {CATEGORIES.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
        <label>
          Priority
          <select value={form.priority} onChange={(e) => update("priority", e.target.value)}>
            {PRIORITIES.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </label>
      </div>
      <button className="btn btn-primary" type="submit" disabled={submitting}>
        {submitting ? "Saving…" : "Create ticket"}
      </button>
    </form>
  );
}
