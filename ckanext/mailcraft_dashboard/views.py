from __future__ import annotations

from flask import Blueprint
from flask.views import MethodView

import ckan.plugins.toolkit as tk
from ckan import types

from ckanext.tables.shared import GenericTableView

from ckanext.mailcraft_dashboard.table import DashboardTable

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


def _build_context() -> types.Context:
    return {
        "user": tk.current_user.name,
        "auth_user_obj": tk.current_user,
    }


mailcraft.before_request(before_request)

mailcraft.add_url_rule(
    "/dashboard", view_func=GenericTableView.as_view("dashboard", table=DashboardTable)
)
mailcraft.add_url_rule(
    "/dashboard/read/<mail_id>", view_func=MailReadView.as_view("mail_read")
)
