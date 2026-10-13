import { request } from "./client.js";

export function listTickets(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== "" && v !== undefined && v !== null) query.append(k, v);
  });
  const qs = query.toString();
  return request(`/api/tickets${qs ? `?${qs}` : ""}`);
}

export function getTicket(id) {
  return request(`/api/tickets/${id}`);
}

export function createTicket(payload) {
  return request("/api/tickets", { method: "POST", body: payload });
}

export function updateTicket(id, payload) {
  return request(`/api/tickets/${id}`, { method: "PATCH", body: payload });
}

export function addComment(id, body) {
  return request(`/api/tickets/${id}/comments`, { method: "POST", body: { body } });
}

export function aiSuggest(id) {
  return request(`/api/tickets/${id}/ai-suggest`, { method: "POST" });
}

export function dashboardSummary() {
  return request("/api/dashboard/summary");
}
