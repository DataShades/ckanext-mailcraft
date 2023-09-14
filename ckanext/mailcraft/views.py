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
                    tk.get_action("mailcraft_mail_list")(self._build_context(), {})
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
            tk.h.ap_table_column("id", sortable=False),
            tk.h.ap_table_column("subject", sortable=False),
            tk.h.ap_table_column("sender", sortable=False),
            tk.h.ap_table_column("recipient", sortable=False),
            tk.h.ap_table_column("message", sortable=False),
            tk.h.ap_table_column("timestamp", column_renderer="ap_date", sortable=False),
            # tk.h.ap_table_column(
            #     "actions",
            #     sortable=False,
            #     column_renderer="ap_action_render",
            #     width="10%",
            #     actions=[
            #         tk.h.ap_table_action(
            #             "mailcraft.mail_read",
            #             tk._("View"),
            #             {"mailcraft_id": "$id"},
            #             attributes={"class": "btn btn-danger"},
            #         )
            #     ],
            # ),
        ]
    # subject = Column(Text)
    # timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    # sender = Column(Text)
    # recipient = Column(Text)
    # message = Column(Text)
    # state = Column(Text, nullable=False, default=State.success)
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
                    tk.get_action("mailcraft_list")(self._build_context(), {})
                ),
                "columns": self._get_table_columns(),
                "bulk_options": self._get_bulk_actions(),
            },
        )

    def _build_context(self) -> types.Context:
        return {
            "user": tk.current_user.name,
            "auth_user_obj": tk.current_user,
        }


class ConfigView(MethodView):
    def get(self) -> str:
        return tk.render("mailcraft/dashboard.html")

    def post(self) -> str:
        return tk.render("mailcraft/dashboard.html")


mailcraft.add_url_rule("/config", view_func=ConfigView.as_view("config"))
mailcraft.add_url_rule("/dashboard", view_func=DashboardView.as_view("dashboard"))


def get_blueprints():
    return [mailcraft]
