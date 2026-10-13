from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import relationship

from app.db.base import Base

PRIORITIES = ("Low", "Medium", "High", "Urgent")
CATEGORIES = ("general", "billing", "account", "technical", "bug", "other")
STATUSES = ("Open", "In Progress", "Waiting", "Resolved", "Closed")

# Allowed workflow transitions. Anything not listed here is rejected.
STATUS_TRANSITIONS = {
    "Open": ("In Progress", "Closed"),
    "In Progress": ("Waiting", "Resolved"),
    "Waiting": ("In Progress", "Resolved"),
    "Resolved": ("Closed", "In Progress"),
    "Closed": ("Open",),
}


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="general")
    priority = Column(String(20), nullable=False, default="Medium")
    status = Column(String(20), nullable=False, default="Open")
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assignee_id])
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")
    events = relationship("TicketEvent", back_populates="ticket", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_tickets_status", "status"),
        Index("ix_tickets_assignee_status", "assignee_id", "status"),
        Index("ix_tickets_requester_created", "requester_id", "created_at"),
    )
