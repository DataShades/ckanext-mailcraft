from __future__ import annotations

import logging
from typing import Any

from sqlalchemy import Column, DateTime, Integer, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Query
from typing_extensions import Self

from ckan import model, types
from ckan.plugins import toolkit as tk

from ckanext.mailcraft.types import EmailData

log = logging.getLogger(__name__)


class Email(tk.BaseModel):
    __tablename__ = "mailcraft_mail"

    class State:
        failed = "failed"
        success = "success"
        stopped = "stopped"

    id = Column(Integer, primary_key=True)

    subject = Column(Text)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    sender = Column(Text)
    recipient = Column(Text)
    message = Column(Text)
    state = Column(Text, nullable=False, default=State.success)
    extras = Column("extras", MutableDict.as_mutable(JSONB))

    @classmethod
    def all(cls) -> list[dict[str, Any]]:
        query: Query = model.Session.query(cls).order_by(cls.timestamp.desc())

        return [mail.dictize({}) for mail in query.all()]

    @classmethod
    def create(cls, **kwargs: Any) -> Email:
        mail = cls(**kwargs)

        model.Session.add(mail)
        model.Session.commit()

        return mail

    @classmethod
    def save_mail(
        cls,
        email_data: EmailData,
        body_html: str,
        state: str,
    ) -> Email:
        mail = cls(
            subject=email_data["Subject"],
            timestamp=email_data["Date"],
            sender=email_data["From"],
            recipient=email_data["To"],
            message=body_html,
            state=state,
            extras=email_data,
        )

        model.Session.add(mail)
        model.Session.commit()

        return mail

    def dictize(self, context: types.Context) -> dict[str, Any]:
        return {
            "id": self.id,
            "subject": self.subject,
            "timestamp": self.timestamp.isoformat(),
            "sender": self.sender,
            "recipient": self.recipient,
            "message": self.message,
            "state": self.state,
            "extras": self.extras or {},
        }

    @classmethod
    def clear_emails(cls) -> int:
        rows_deleted = model.Session.query(cls).delete()
        model.Session.commit()

        return rows_deleted

    @classmethod
    def get(cls, mail_id: str) -> Self | None:
        query: Query = model.Session.query(cls).filter(cls.id == mail_id)

        return query.one_or_none()

    def delete(self) -> None:
        model.Session().autoflush = False
        model.Session.delete(self)
