from __future__ import annotations

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.tables.shared import GenericTableView

from ckanext.mailcraft.utils import get_mailer

mailcraft = Blueprint("mailcraft", __name__, url_prefix="/ckan-admin/mailcraft")


def before_request() -> None:
    try:
        tk.check_access("sysadmin", {"user": tk.current_user.name})
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


class MailReadView(MethodView):
    """View for reading a single email."""

    def get(self, mail_id: str) -> str:
        """Render the email reading template."""
        try:
            mail = tk.get_action("mc_mail_show")(_build_context(), {"id": mail_id})
        except tk.ValidationError:
            return tk.render("mailcraft/404.html")

        return tk.render("mailcraft/mail_read.html", extra_vars={"mail": mail})


class MailClearView(MethodView):
    """View for clearing all emails."""

    def post(self) -> Response:
        """Clear all emails and redirect to the dashboard."""
        tk.get_action("mc_mail_clear")(_build_context(), {})

        return tk.redirect_to("mailcraft.dashboard")


class MailTestView(MethodView):
    """View for sending a test email."""

    def post(self) -> Response:
        """Send a test email and redirect to the dashboard."""
        mailer = get_mailer()

        mailer.mail_recipients(
            subject="Hello world",
            recipients=["test@gmail.com"],
            body="Hello world",
            body_html=tk.render(
                "mailcraft/emails/test.html",
                extra_vars={
                    "site_url": mailer.site_url,
                    "site_title": mailer.site_title,
                },
            ),
        )

        return tk.redirect_to("mailcraft.dashboard")


def _build_context() -> types.Context:
    return {
        "user": tk.current_user.name,
        "auth_user_obj": tk.current_user,
    }


mailcraft.before_request(before_request)

mailcraft.add_url_rule("/test", view_func=MailTestView.as_view("send_test"))
mailcraft.add_url_rule(
    "/dashboard", view_func=GenericTableView.as_view("dashboard", table="mailcraft")
)
mailcraft.add_url_rule(
    "/dashboard/read/<mail_id>", view_func=MailReadView.as_view("mail_read")
)
mailcraft.add_url_rule(
    "/dashboard/clear", view_func=MailClearView.as_view("clear_mails")
)
