from __future__ import annotations

import codecs
import logging
import mimetypes
import os
import smtplib
import base64
from abc import ABC, abstractmethod
from collections.abc import Iterable
from email import utils as email_utils
from email.message import EmailMessage
from time import time
from typing import Any

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan import model

import ckanext.mailcraft.config as mc_config
import ckanext.mailcraft_dashboard.model as mc_model
from ckanext.mailcraft.exception import MailerException
from ckanext.mailcraft.types import Attachment, AttachmentData, EmailData

log = logging.getLogger(__name__)


class BaseMailer(ABC):
    """Base class for mailers."""

    def __init__(self):
        """Initialize the mailer with SMTP settings from CKAN config."""
        self.server = tk.config["smtp.server"]
        self.start_tls = tk.asbool(tk.config["smtp.starttls"])
        self.user = tk.config["smtp.user"]
        self.password = tk.config["smtp.password"]
        self.mail_from = tk.config["smtp.mail_from"]
        self.reply_to = tk.config["smtp.reply_to"]

        self.site_title = tk.config["ckan.site_title"]
        self.site_url = tk.config["ckan.site_url"]

        self.conn_timeout = mc_config.get_conn_timeout()
        self.stop_outgoing = mc_config.stop_outgoing_emails()
        self.save_emails = mc_config.save_emails_to_db()
        self.redirect_to = mc_config.get_redirect_email()
        self.store_att_content = mc_config.store_attachments_content()

    @abstractmethod
    def mail_recipients(  # noqa: PLR0913
        self,
        subject: str,
        recipients: list[str],
        body: str,
        body_html: str,
        headers: dict[str, Any] | None = None,
        attachments: Iterable[Attachment] | None = None,
        to: list[str] | None = None,
    ) -> bool:
        """Send an email to a list of recipients."""

    @abstractmethod
    def add_attachments(
        self, msg: EmailMessage, attachments: Iterable[Attachment]
    ) -> None:
        """Add attachments to the email message."""

    @abstractmethod
    def get_connection(self) -> smtplib.SMTP:
        """Get an SMTP connection object."""

    @abstractmethod
    def test_conn(self):
        """Test the SMTP connection."""

    @abstractmethod
    def mail_user(  # noqa: PLR0913
        self,
        user: str,
        subject: str,
        body: str,
        body_html: str,
        headers: dict[str, Any] | None = None,
        attachments: Iterable[Attachment] | None = None,
    ) -> bool:
        """Send an email to a CKAN user by their ID or name."""


class DefaultMailer(BaseMailer):
    """Default mailer implementation."""

    def mail_recipients(  # noqa: PLR0913, C901
        self,
        subject: str,
        recipients: list[str],
        body: str,
        body_html: str,
        headers: dict[str, Any] | None = None,
        attachments: Iterable[Attachment] | None = None,
        to: list[str] | None = None,
    ) -> bool:
        """Send an email to a list of recipients."""
        headers = headers or {}
        attachments = attachments or []

        if self.redirect_to:
            log.info(
                "Redirecting email to %s instead of %s", self.redirect_to, recipients
            )
            recipients = self.redirect_to

        msg = EmailMessage()

        msg["From"] = email_utils.formataddr((self.site_title, self.mail_from))
        msg["Subject"] = subject
        msg["Date"] = email_utils.formatdate(time())
        msg["To"] = ", ".join(to) if to else ", ".join(recipients)

        if not tk.config.get("ckan.hide_version"):
            msg["X-Mailer"] = f"CKAN {tk.h.ckan_version()}"

        for k, v in headers.items():
            msg.replace_header(k, v) if k in msg else msg.add_header(k, v)

        # Assign Reply-to if configured and not set via headers
        if self.reply_to and not msg["Reply-to"]:
            msg["Reply-to"] = self.reply_to

        msg.set_content(body, cte="base64")
        msg.add_alternative(body_html, subtype="html", cte="base64")

        if attachments:
            self.add_attachments(msg, attachments)

        try:
            if self.stop_outgoing:
                self._save_email(msg, body_html, mc_model.Email.State.stopped)
            else:
                self._send_email(recipients, msg)
        except MailerException:
            log.exception("Error sending email to %s", recipients)
            self._save_email(msg, body_html, mc_model.Email.State.failed)
            return False
        else:
            if not self.stop_outgoing:
                self._save_email(msg, body_html)

        return True

    def add_attachments(
        self, msg: EmailMessage, attachments: Iterable[Attachment]
    ) -> None:
        """Add attachments to the email message."""
        for attachment in attachments:
            name = attachment["name"]
            content = attachment["content"]
            media_type = attachment.get("media_type")
            cid = attachment.get("cid")
            disposition = attachment.get("disposition")

            # Guess media type if not provided
            if not media_type:
                media_type, _ = mimetypes.guess_type(name)

            main_type, sub_type = (
                media_type.split("/") if media_type else ("application", "octet-stream")
            )

            # Add the attachment first
            msg.add_attachment(
                content,
                maintype=main_type,
                subtype=sub_type,
                filename=name,
                disposition=disposition or ("inline" if cid else "attachment"),
                cid=cid if cid else None,
            )

    def collect_attachments(self, msg: EmailMessage) -> list[AttachmentData]:
        """Collect attachments from the email message."""
        attachments = []
        for part in msg.walk():
            if part.is_multipart():
                continue

            filename = part.get_filename()

            if not filename:
                continue

            content_id = part.get("Content-ID")
            disposition = part.get_content_disposition()
            content_type = part.get_content_type()
            payload = part.get_payload(decode=True)

            attachments.append(
                AttachmentData(
                    filename=filename if filename else "unknown",
                    content_id=content_id,
                    disposition=disposition or "attachment",
                    content_type=content_type,
                    size=len(payload) if payload else 0,
                    data=base64.b64encode(payload).decode("utf-8") if self.store_att_content else None,  # type: ignore
                )
            )
        return attachments

    def get_connection(self) -> smtplib.SMTP:
        """Get an SMTP conn object."""
        try:
            conn = smtplib.SMTP(self.server, timeout=self.conn_timeout)
        except OSError as e:
            log.exception('SMTP server could not be connected to: "%s"', self.server)
            raise MailerException(  # noqa: TRY003
                'SMTP server could not be connected to: "%s" %s', self.server, e
            ) from e

        try:
            conn.ehlo()

            if self.start_tls:
                if conn.has_extn("STARTTLS"):
                    conn.starttls()
                    conn.ehlo()
                else:
                    raise MailerException(  # noqa: TRY003
                        "SMTP server does not support STARTTLS"
                    )

            if self.user:
                conn.login(self.user, self.password)
        except smtplib.SMTPException as e:
            log.exception("An error occurred during SMTP authentication")
            raise MailerException(f"{e}") from e

        return conn

    def _save_email(
        self,
        msg: EmailMessage,
        body_html: str,
        state: str = mc_model.Email.State.success,
    ) -> None:
        if not p.plugin_loaded("mailcraft_dashboard") or not self.save_emails:
            return

        attachments_data = self.collect_attachments(msg)
        email_data: EmailData = dict(msg.items())  # type: ignore
        email_data["attachments"] = attachments_data

        mc_model.Email.save_mail(email_data, body_html, state)

    def _send_email(self, recipients: list[str], msg: EmailMessage):
        conn = self.get_connection()

        try:
            conn.sendmail(self.mail_from, recipients, msg.as_string())
            log.info("Sent email to %s", recipients)
        except smtplib.SMTPException as e:
            log.exception("Error sending email: %s")
            raise MailerException("Error sending email: %s", e) from e  # noqa: TRY003
        finally:
            conn.quit()

    def test_conn(self):
        """Test the SMTP connection."""
        conn = self.get_connection()
        conn.quit()

    def mail_user(  # noqa: PLR0913
        self,
        user: str,
        subject: str,
        body: str,
        body_html: str,
        headers: dict[str, Any] | None = None,
        attachments: Iterable[Attachment] | None = None,
    ) -> bool:
        """Sends an email to a CKAN user by its ID or name."""
        user_obj = model.User.get(user)

        if not user_obj:
            raise MailerException(tk._("User doesn't exist"))

        if not user_obj.email:
            raise MailerException(tk._("User doesn't have an email address"))

        return self.mail_recipients(
            subject,
            [user_obj.email],
            body,
            body_html=body_html,
            headers=headers,
            attachments=attachments,
        )

    def send_reset_link(self, user: model.User) -> None:
        """Sends a password reset link to a user.

        Args:
            user: The user to send the reset link to.
        """
        self.create_reset_key(user)
        extra_vars = {
            "reset_link": tk.h.url_for(
                "user.perform_reset", id=user.id, key=user.reset_key, qualified=True
            ),
            "site_title": tk.config.get("ckan.site_title"),
            "site_url": tk.config.get("ckan.site_url"),
            "user_name": user.name,
        }

        self.mail_user(
            user=user.name,
            subject="Reset your password",
            body=tk.render(
                "mailcraft/emails/reset_password/body.txt",
                extra_vars,
            ),
            body_html=tk.render(
                "mailcraft/emails/reset_password/body.html",
                extra_vars,
            ),
        )

    def create_reset_key(self, user: model.User):
        """Creates a reset key for a user and saves it to the database."""
        user.reset_key = codecs.encode(os.urandom(16), "hex").decode()
        model.repo.commit_and_remove()

    def verify_reset_link(self, user: model.User, key: str | None) -> bool:
        """Verifies if the reset key is valid for the user."""
        if not key or not user.reset_key:
            return False

        return key.strip() == user.reset_key
