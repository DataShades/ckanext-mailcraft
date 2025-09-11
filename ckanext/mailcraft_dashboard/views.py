from __future__ import annotations

from typing import Any

from ckanext.mailcraft.utils import get_mailer
from ckanext.mailcraft_dashboard.generics import ApTableView
from ckanext.mailcraft_dashboard.table import (
    ActionDefinition,
    ColumnDefinition,
    GlobalActionDefinition,
    GlobalActionHandler,
    GlobalActionHandlerResult,
    Row,
    TableDefinition,
)

import ckan.plugins.toolkit as tk
from ckan import types
from flask import Blueprint, Response
from flask.views import MethodView

mailcraft = Blueprint("mailcraft", __name__, url_prefix="/ckan-admin/mailcraft")


def before_request() -> None:
    """A before request handler to check for sysadmin rights."""
    try:
        tk.check_access("sysadmin", {"user": tk.current_user.name})
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


class DashboardTable(TableDefinition):
    """Table definition for the mailcraft dashboard."""

    def __init__(self):
        """Initialize the table definition."""
        super().__init__(
            name="content",
            ajax_url=tk.url_for("mailcraft.dashboard", data=True),
            columns=[
                ColumnDefinition(field="id", filterable=False, resizable=False),
                ColumnDefinition(field="subject", width=250),
                ColumnDefinition(field="sender"),
                ColumnDefinition(field="recipient"),
                ColumnDefinition(field="state", resizable=False, width=100),
                ColumnDefinition(
                    field="timestamp",
                    formatters=[("date", {"date_format": "%Y-%m-%d %H:%M"})],
                    resizable=False,
                ),
                ColumnDefinition(
                    field="actions",
                    formatters=[("actions", {})],
                    filterable=False,
                    tabulator_formatter="html",
                    sorter=None,
                    resizable=False,
                ),
            ],
            actions=[
                ActionDefinition(
                    name="view",
                    label=tk._("View"),
                    icon="fa fa-eye",
                    endpoint="mailcraft.mail_read",
                    url_params={
                        "view": "read",
                        "mail_id": "$id",
                    },
                ),
            ],
            global_actions=[
                GlobalActionDefinition(
                    action="delete", label="Delete selected entities"
                ),
            ],
            table_action_snippet="mailcraft/table_actions.html",
        )

    def get_raw_data(self) -> list[dict[str, Any]]:
        """Fetch raw data for the table."""
        return tk.get_action("mc_mail_list")(_build_context(), {})


class DashboardView(ApTableView):
    """View for the mailcraft dashboard."""

    def get_global_action(self, value: str) -> GlobalActionHandler | None:
        """Return the handler for a global action."""
        return {"delete": self._remove_emails}.get(value)

    @staticmethod
    def _remove_emails(row: Row) -> GlobalActionHandlerResult:
        try:
            tk.get_action("mc_mail_delete")(
                {"ignore_auth": True},
                {"id": row["id"]},
            )
        except tk.ObjectNotFound:
            return False, tk._("Mail not found")

        return True, None


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


mailcraft.add_url_rule("/test", view_func=MailTestView.as_view("send_test"))
mailcraft.add_url_rule(
    "/dashboard",
    view_func=DashboardView.as_view(
        "dashboard",
        table=DashboardTable,
        page_title="",
    ),
)
mailcraft.add_url_rule(
    "/dashboard/read/<mail_id>", view_func=MailReadView.as_view("mail_read")
)
mailcraft.add_url_rule(
    "/dashboard/clear", view_func=MailClearView.as_view("clear_mails")
)
