const CLASS = {
  Open: "badge badge-open",
  "In Progress": "badge badge-progress",
  Waiting: "badge badge-waiting",
  Resolved: "badge badge-resolved",
  Closed: "badge badge-closed",
};

export default function StatusBadge({ value }) {
  return <span className={CLASS[value] || "badge"}>{value}</span>;
}
