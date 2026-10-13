import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext.jsx";

export default function NavBar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <div className="container navbar-inner">
        <Link to="/" className="brand">
          AI Support Desk
        </Link>
        {user && (
          <nav className="nav-links">
            <Link to="/">Dashboard</Link>
            <Link to="/tickets">Tickets</Link>
            <Link to="/tickets/new">New Ticket</Link>
            <span className="user-chip">
              {user.full_name} · {user.role}
            </span>
            <button className="btn btn-ghost" onClick={handleLogout}>
              Logout
            </button>
          </nav>
        )}
      </div>
    </header>
  );
}
