from __future__ import annotations

from typing import Any

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
import ckan.types as types

from ckanext.ap_main.utils import ap_before_request
from ckanext.ap_main.views.generics import ApConfigurationPageView, ApTableView
import ckanext.ap_main.types as ap_types
from ckanext.ap_main.table import (
    ActionDefinition,
    ColumnDefinition,
    GlobalActionDefinition,
    TableDefinition,
)

from ckanext.mailcraft.utils import get_mailer

mailcraft = Blueprint("mailcraft", __name__, url_prefix="/admin-panel/mailcraft")
mailcraft.before_request(ap_before_request)


class DashboardTable(TableDefinition):
    def __init__(self):
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
        return tk.get_action("mc_mail_list")(_build_context(), {})


class DashboardView(ApTableView):
    def get_global_action(self, value: str) -> ap_types.GlobalActionHandler | None:
        return {"delete": self._remove_emails}.get(value)

    @staticmethod
    def _remove_emails(row: ap_types.Row) -> ap_types.GlobalActionHandlerResult:
        try:
            tk.get_action("mc_mail_delete")(
                {"ignore_auth": True},
                {"id": row["id"]},
            )
        except tk.ObjectNotFound:
            return False, tk._("Mail not found")

        return True, None


class MailReadView(MethodView):
    def get(self, mail_id: str) -> str:
        try:
            mail = tk.get_action("mc_mail_show")(_build_context(), {"id": mail_id})
        except tk.ValidationError:
            return tk.render("mailcraft/404.html")

        return tk.render("mailcraft/mail_read.html", extra_vars={"mail": mail})


class MailClearView(MethodView):
    def post(self) -> str:
        tk.get_action("mc_mail_clear")(_build_context(), {})

        return ""


def _build_context() -> types.Context:
    return {
        "user": tk.current_user.name,
        "auth_user_obj": tk.current_user,
    }


def send_test_email() -> Response:
    """Send a test email"""
    mailer = get_mailer()

    mailer.mail_recipients(
        subject="Hello world",
        recipients=["test@gmail.com"],
        body="Hello world",
        body_html=tk.render(
            "mailcraft/emails/test.html",
            extra_vars={"site_url": mailer.site_url, "site_title": mailer.site_title},
        ),
    )

    tk.h.flash_success(tk._("Test email has been sent"))

    return tk.redirect_to("mailcraft.dashboard")


mailcraft.add_url_rule("/test", endpoint="test", view_func=send_test_email)
mailcraft.add_url_rule(
    "/dashboard", view_func=DashboardView.as_view("dashboard", table=DashboardTable)
)
mailcraft.add_url_rule(
    "/config",
    view_func=ApConfigurationPageView.as_view("config", "mailcraft_config"),
)
mailcraft.add_url_rule(
    "/dashboard/read/<mail_id>", view_func=MailReadView.as_view("mail_read")
)
mailcraft.add_url_rule(
    "/dashboard/clear", view_func=MailClearView.as_view("clear_mails")
)


def get_blueprints():
    return [mailcraft]
