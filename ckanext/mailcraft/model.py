from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, Integer, Text
from sqlalchemy.orm import Query

import ckan.model as model
from ckan.plugins import toolkit as tk

log = logging.getLogger(__name__)


class Email(tk.BaseModel):
    __tablename__ = "mailcraft_mail"

    class State:
        failed = "failed"
        success = "success"

    id = Column(Integer, primary_key=True)

    subject = Column(Text)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    sender = Column(Text)
    recipient = Column(Text)
    message = Column(Text)
    state = Column(Text, nullable=False, default=State.success)

    @classmethod
    def all(cls) -> list[dict[str, Any]]:
        query: Query = model.Session.query.query(cls).order_by(cls.timestamp.desc())

        return [mail.dictize({}) for mail in query.all()]

    @classmethod
    def save_log(cls, record: logging.LogRecord, message_formatted: str) -> None:
        model.Session.query.add(
            cls(
                name=record.name,
                path=record.pathname,
                level=record.levelno,
                message=record.getMessage(),
                message_formatted=message_formatted,
            )
        )
        model.Session.query.commit()

    def dictize(self, context):
        return {
            "subject": self.subject,
            "timestamp": self.timestamp,
            "recipient": self.recipient,
            "message": self.message,
        }

    @classmethod
    def clear_emails(cls) -> int:
        rows_deleted = model.Session.query.query(cls).delete()
        model.Session.query.commit()

        return rows_deleted
