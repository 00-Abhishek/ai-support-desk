from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_staff
from app.db.session import get_db
from app.models.user import User
from app.schemas.ticket import (
    AISuggestion,
    CommentCreate,
    CommentOut,
    TicketCreate,
    TicketDetail,
    TicketList,
    TicketOut,
    TicketUpdate,
)
from app.services import ai_service, ticket_service

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


@router.post("", response_model=TicketOut, status_code=status.HTTP_201_CREATED)
def create_ticket(payload: TicketCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ticket_service.create_ticket(db, payload, user)


@router.get("", response_model=TicketList)
def list_tickets(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    priority: Optional[str] = None,
    category: Optional[str] = None,
    assignee_id: Optional[int] = None,
    search: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
):
    total, items = ticket_service.list_tickets(
        db,
        status=status_filter,
        priority=priority,
        category=category,
        assignee_id=assignee_id,
        search=search,
        limit=limit,
        offset=offset,
    )
    return TicketList(total=total, items=items)


@router.get("/{ticket_id}", response_model=TicketDetail)
def get_ticket(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return ticket_service.get_ticket(db, ticket_id)


@router.patch("/{ticket_id}", response_model=TicketOut)
def update_ticket(
    ticket_id: int,
    payload: TicketUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_staff),
):
    return ticket_service.update_ticket(db, ticket_id, payload, user)


@router.post("/{ticket_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def add_comment(
    ticket_id: int,
    payload: CommentCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return ticket_service.add_comment(db, ticket_id, payload.body, user)


@router.post("/{ticket_id}/ai-suggest", response_model=AISuggestion)
def ai_suggest(ticket_id: int, db: Session = Depends(get_db), user: User = Depends(require_staff)):
    ticket = ticket_service.get_ticket(db, ticket_id)
    return ai_service.suggest(ticket.title, ticket.description)
