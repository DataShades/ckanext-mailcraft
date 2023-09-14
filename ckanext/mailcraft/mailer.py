from __future__ import annotations

import logging
import mimetypes
import smtplib
import socket
from email import utils as email_utils
from email.message import EmailMessage
from time import time
from typing import Any, Iterable, Optional, cast

import ckan.model as model
import ckan.plugins.toolkit as tk

import ckanext.mailcraft.config as mc_config
from ckanext.mailcraft.exception import MailerException
from ckanext.mailcraft.types import (Attachment, AttachmentWithoutType,
                                     AttachmentWithType)

log = logging.getLogger(__name__)


class DefaultMailer:
    def __init__(self):
        self.server = tk.config["smtp.server"]
        self.start_tls = tk.config["smtp.starttls"]
        self.user = tk.config["smtp.user"]
        self.password = tk.config["smtp.password"]
        self.mail_from = tk.config["smtp.mail_from"]
        self.reply_to = tk.config["smtp.reply_to"]

        self.site_title = tk.config["ckan.site_title"]
        self.site_url = tk.config["ckan.site_url"]

        self.conn_timeout = mc_config.get_conn_timeout()

    def mail_recipients(
        self,
        subject: str,
        recipients: list[str],
        body: str,
        body_html: str,
        headers: Optional[dict[str, Any]] = None,
        attachments: Optional[Iterable[Attachment]] = None,
    ):
        headers = headers or {}
        attachments = attachments or []

        msg = EmailMessage()

        msg["From"] = email_utils.formataddr((self.site_title, self.mail_from))
        msg["To"] = msg["Bcc"] = ", ".join(recipients)
        # msg['To'] = email_utils.formataddr((recipient_name, recipient_email))
        msg["Subject"] = subject
        msg["Date"] = email_utils.formatdate(time())

        if not tk.config.get("ckan.hide_version"):
            msg["X-Mailer"] = f"CKAN {tk.h.ckan_version()}"

        for k, v in headers.items():
            msg.replace_header(k, v) if k in msg.keys() else msg.add_header(k, v)

        # Assign Reply-to if configured and not set via headers
        if self.reply_to and not msg["Reply-to"]:
            msg["Reply-to"] = self.reply_to

        msg.set_content(body, cte="base64")
        msg.add_alternative(body_html, subtype="html", cte="base64")

        if attachments:
            self._add_attachments(msg, attachments)

        self._send_email(recipients, msg)

    def _add_attachments(self, msg: EmailMessage, attachments) -> None:
        """Add attachments on an email message
        If attachment length is 3, it means, that this is an attachment with type"""

        for attachment in attachments:
            if len(attachment) == 3:
                name, _file, media_type = cast(AttachmentWithType, attachment)
            else:
                name, _file = cast(AttachmentWithoutType, attachment)
                media_type = None

            if not media_type:
                media_type, _ = mimetypes.guess_type(name)

            main_type, sub_type = media_type.split("/") if media_type else (None, None)

            msg.add_attachment(
                _file.read(),
                filename=name,
                maintype=main_type,
                subtype=sub_type,
            )

    def get_connection(self) -> smtplib.SMTP:
        """Get an SMTP conn object"""
        try:
            conn = smtplib.SMTP(self.server, timeout=self.conn_timeout)
        except (socket.error, smtplib.SMTPConnectError) as e:
            log.exception(e)
            raise MailerException(
                f'SMTP server could not be connected to: "{self.server}" {e}'
            )

        try:
            conn.ehlo()

            if self.start_tls:
                if conn.has_extn("STARTTLS"):
                    conn.starttls()
                    conn.ehlo()
                else:
                    raise MailerException("SMTP server does not support STARTTLS")

            if self.user:
                assert self.password, (
                    "If smtp.user is configured then "
                    "smtp.password must be configured as well."
                )
                conn.login(self.user, self.password)
        except smtplib.SMTPException as e:
            log.exception(f"{e}")
            raise MailerException(f"{e}")

        return conn

    def _send_email(self, recipients, msg: EmailMessage):
        conn = self.get_connection()

        try:
            conn.sendmail(self.mail_from, recipients, msg.as_string())
            log.info(f"Sent email to {recipients}")
        except smtplib.SMTPException as e:
            log.exception(f"{e}")
            raise MailerException(f"{e}")
        finally:
            conn.quit()

    def test_conn(self):
        conn = self.get_connection()
        conn.quit()

    def mail_user(
        self,
        user: str,
        subject: str,
        body: str,
        body_html: str,
        headers: Optional[dict[str, Any]] = None,
        attachments: Optional[Iterable[Attachment]] = None,
    ) -> None:
        """Sends an email to a CKAN user by its ID or name"""
        user_obj = model.User.get(user)

        if not user_obj:
            raise MailerException(tk._("User doesn't exist"))

        if not user_obj.email:
            raise MailerException(tk._("User doesn't have an email address"))

        self.mail_recipients(
            # user_obj.display_name,
            subject,
            [user_obj.email],
            body,
            body_html=body_html,
            headers=headers,
            attachments=attachments,
        )

    # You can add more methods for different types of emails
    # (e.g., password reset, notifications).

    # def send_password_reset_email(self, user):
    #     subject = "Password Reset Request"
    #     recipients = [user.email]
    #     template = "email/password_reset.html"
    #     self.send_email(subject, recipients, template, user=user)

    # def send_notification_email(self, user, msg):
    #     subject = "Notification"
    #     recipients = [user.email]
    #     template = "email/notification.html"
    #     self.send_email(subject, recipients, template, user=user, msg=msg)
