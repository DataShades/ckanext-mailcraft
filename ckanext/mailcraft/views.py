from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
import ckan.types as types
from ckan.lib.helpers import Page
from flask import Blueprint
from flask.views import MethodView

from ckanext.admin_panel.utils import ap_before_request

import ckanext.mailcraft.config as mc_config

mailcraft = Blueprint("mailcraft", __name__, url_prefix="/mailcraft")
mailcraft.before_request(ap_before_request)


class DashboardView(MethodView):
    def get(self) -> str:
        return tk.render(
            "mailcraft/dashboard.html",
            extra_vars={
                "page": self._get_pager(
                    tk.get_action("mc_mail_list")(_build_context(), {})
                ),
                "columns": self._get_table_columns(),
                "bulk_options": self._get_bulk_actions(),
            },
        )

    def _get_pager(self, mailcraft_list: list[dict[str, Any]]) -> Page:
        return Page(
            collection=mailcraft_list,
            page=tk.h.get_page_number(tk.request.args),
            url=tk.h.pager_url,
            item_count=len(mailcraft_list),
            items_per_page=mc_config.get_mail_per_page(),
        )

    def _get_table_columns(self) -> list[dict[str, Any]]:
        return [
            tk.h.ap_table_column("id", sortable=False, width="5%"),
            tk.h.ap_table_column("subject", sortable=False, width="10%"),
            tk.h.ap_table_column("sender", sortable=False, width="10%"),
            tk.h.ap_table_column("recipient", sortable=False, width="20%"),
            tk.h.ap_table_column("message", sortable=False, width="30%"),
            tk.h.ap_table_column("state", sortable=False, width="5%"),
            tk.h.ap_table_column(
                "timestamp", column_renderer="ap_date", sortable=False, width="10%"
            ),
            tk.h.ap_table_column(
                "actions",
                sortable=False,
                width="10%",
                column_renderer="ap_action_render",
                actions=[
                    tk.h.ap_table_action(
                        "mailcraft.mail_read",
                        tk._("View"),
                        {"mail_id": "$id"},
                        attributes={"class": "btn btn-primary"},
                    )
                ],
            ),
        ]

    def _get_bulk_actions(self):
        return [
            {
                "value": "1",
                "text": tk._("Remove selected mails"),
            },
        ]

    def post(self):
        return tk.render(
            "mailcraft/mailcraft_list.html",
            extra_vars={
                "page": self._get_pager(
                    tk.get_action("mailcraft_list")(_build_context(), {})
                ),
                "columns": self._get_table_columns(),
                "bulk_options": self._get_bulk_actions(),
            },
        )


class ConfigView(MethodView):
    def get(self) -> str:
        return tk.render("mailcraft/dashboard.html")

    def post(self) -> str:
        return tk.render("mailcraft/dashboard.html")


class MailReadView(MethodView):
    def get(self, mail_id: str) -> str:
        try:
            mail = tk.get_action("mc_mail_show")(_build_context(), {"id": mail_id})
        except tk.ValidationError:
            return tk.render("mailcraft/404.html")

        return tk.render("mailcraft/mail_read.html", extra_vars={"mail": mail})


def _build_context() -> types.Context:
    return {
        "user": tk.current_user.name,
        "auth_user_obj": tk.current_user,
    }


mailcraft.add_url_rule("/config", view_func=ConfigView.as_view("config"))
mailcraft.add_url_rule("/dashboard", view_func=DashboardView.as_view("dashboard"))
mailcraft.add_url_rule(
    "/dashboard/read/<mail_id>", view_func=MailReadView.as_view("mail_read")
)


def get_blueprints():
    return [mailcraft]
