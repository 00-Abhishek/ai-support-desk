from typing import Optional

from fastapi import HTTPException, status as http_status
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.event import TicketEvent
from app.models.ticket import (
    CATEGORIES,
    PRIORITIES,
    STATUS_TRANSITIONS,
    STATUSES,
    Ticket,
)
from app.models.user import User
from app.schemas.ticket import TicketCreate, TicketUpdate


def _record(db: Session, ticket_id: int, actor_id: Optional[int], event_type: str, detail: str = None):
    db.add(TicketEvent(ticket_id=ticket_id, actor_id=actor_id, event_type=event_type, detail=detail))


def _validate_enum(value: str, allowed, field: str):
    if value not in allowed:
        raise HTTPException(
            status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid {field} '{value}'. Allowed: {', '.join(allowed)}",
        )


def create_ticket(db: Session, payload: TicketCreate, requester: User) -> Ticket:
    _validate_enum(payload.priority, PRIORITIES, "priority")
    _validate_enum(payload.category, CATEGORIES, "category")

    ticket = Ticket(
        title=payload.title,
        description=payload.description,
        category=payload.category,
        priority=payload.priority,
        status="Open",
        requester_id=requester.id,
    )
    db.add(ticket)
    db.flush()
    _record(db, ticket.id, requester.id, "created", f"Ticket created by {requester.email}")
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: int) -> Ticket:
    ticket = db.get(Ticket, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    return ticket


def list_tickets(
    db: Session,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assignee_id: Optional[int] = None,
    requester_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    limit = max(1, min(limit, 100))
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if priority:
        stmt = stmt.where(Ticket.priority == priority)
    if category:
        stmt = stmt.where(Ticket.category == category)
    if assignee_id is not None:
        stmt = stmt.where(Ticket.assignee_id == assignee_id)
    if requester_id is not None:
        stmt = stmt.where(Ticket.requester_id == requester_id)
    if search:
        like = f"%{search}%"
        stmt = stmt.where(Ticket.title.ilike(like) | Ticket.description.ilike(like))

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(Ticket.created_at.desc()).limit(limit).offset(offset)
    items = list(db.scalars(stmt).all())
    return total, items


def update_ticket(db: Session, ticket_id: int, payload: TicketUpdate, actor: User) -> Ticket:
    ticket = get_ticket(db, ticket_id)

    if payload.priority is not None:
        _validate_enum(payload.priority, PRIORITIES, "priority")
        if payload.priority != ticket.priority:
            _record(db, ticket.id, actor.id, "priority_changed", f"{ticket.priority} -> {payload.priority}")
            ticket.priority = payload.priority

    if payload.category is not None:
        _validate_enum(payload.category, CATEGORIES, "category")
        ticket.category = payload.category

    if payload.status is not None and payload.status != ticket.status:
        _validate_enum(payload.status, STATUSES, "status")
        allowed = STATUS_TRANSITIONS.get(ticket.status, ())
        if payload.status not in allowed:
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Illegal transition {ticket.status} -> {payload.status}. Allowed: {', '.join(allowed) or 'none'}",
            )
        _record(db, ticket.id, actor.id, "status_changed", f"{ticket.status} -> {payload.status}")
        ticket.status = payload.status

    if payload.assignee_id is not None:
        assignee = db.get(User, payload.assignee_id)
        if assignee is None:
            raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail="Assignee not found")
        if assignee.role not in ("agent", "admin"):
            raise HTTPException(
                status_code=http_status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only agents or admins can be assigned a ticket",
            )
        if assignee.id != ticket.assignee_id:
            _record(db, ticket.id, actor.id, "assigned", f"Assigned to {assignee.email}")
            ticket.assignee_id = assignee.id

    if payload.title is not None:
        ticket.title = payload.title
    if payload.description is not None:
        ticket.description = payload.description

    db.commit()
    db.refresh(ticket)
    return ticket


def add_comment(db: Session, ticket_id: int, body: str, author: User) -> Comment:
    ticket = get_ticket(db, ticket_id)
    comment = Comment(ticket_id=ticket.id, author_id=author.id, body=body)
    db.add(comment)
    _record(db, ticket.id, author.id, "commented", body[:200])
    db.commit()
    db.refresh(comment)
    return comment


def dashboard_counts(db: Session) -> dict:
    rows = db.execute(select(Ticket.status, func.count()).group_by(Ticket.status)).all()
    counts = {s: 0 for s in STATUSES}
    for status_value, count in rows:
        counts[status_value] = count
    return {
        "open": counts["Open"],
        "in_progress": counts["In Progress"],
        "waiting": counts["Waiting"],
        "resolved": counts["Resolved"],
        "closed": counts["Closed"],
        "total": sum(counts.values()),
    }
