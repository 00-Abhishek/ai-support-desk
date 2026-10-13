import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { createTicket } from "../api/tickets.js";
import TicketForm from "../components/TicketForm.jsx";

export default function CreateTicketPage() {
  const navigate = useNavigate();
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(payload) {
    setError("");
    setBusy(true);
    try {
      const ticket = await createTicket(payload);
      navigate(`/tickets/${ticket.id}`);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <h1>Create a ticket</h1>
      <TicketForm onSubmit={handleSubmit} submitting={busy} error={error} />
    </div>
  );
}
