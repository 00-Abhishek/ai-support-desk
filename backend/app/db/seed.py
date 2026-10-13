"""Seed demo users and a few tickets. Safe to run repeatedly."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models.ticket import Ticket
from app.models.user import User

DEMO_USERS = [
    ("admin@example.com", "Ada Admin", "admin", "admin123"),
    ("agent@example.com", "Grace Agent", "agent", "agent123"),
    ("requester@example.com", "Ravi Requester", "requester", "request123"),
]

DEMO_TICKETS = [
    ("I cannot reset my password", "The reset link says expired even right after I request it.", "account", "High", "Open"),
    ("Invoice shows wrong amount", "The March invoice lists 3 seats but we only use 2.", "billing", "Medium", "Open"),
    ("API returns 500 on /orders", "Production outage: /orders returns 500 for all customers.", "technical", "Urgent", "In Progress"),
]


def seed(db: Session) -> None:
    users = {}
    for email, name, role, password in DEMO_USERS:
        user = db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, full_name=name, role=role, hashed_password=hash_password(password))
            db.add(user)
            db.flush()
        users[email] = user

    if db.scalar(select(Ticket).limit(1)) is None:
        requester = users["requester@example.com"]
        agent = users["agent@example.com"]
        for i, (title, desc, cat, prio, st) in enumerate(DEMO_TICKETS):
            ticket = Ticket(
                title=title,
                description=desc,
                category=cat,
                priority=prio,
                status=st,
                requester_id=requester.id,
                assignee_id=agent.id if i == 2 else None,
            )
            db.add(ticket)
    db.commit()
