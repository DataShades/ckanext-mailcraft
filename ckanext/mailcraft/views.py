from __future__ import annotations

from typing import Any, Callable

from flask import Blueprint, Response
from flask.views import MethodView

import ckan.plugins.toolkit as tk
import ckan.types as types
from ckan.lib.helpers import Page
from ckan.logic import parse_params

from ckanext.ap_main.utils import ap_before_request

import ckanext.mailcraft.config as mc_config
from ckanext.collection.shared import get_collection

mailcraft = Blueprint("mailcraft", __name__, url_prefix="/admin-panel/mailcraft")
mailcraft.before_request(ap_before_request)


class DashboardView(MethodView):
    def get(self) -> str:
        return tk.render(
            "mailcraft/dashboard.html",
            extra_vars={
                "collection": get_collection(
                    "mailcraft-dashboard", parse_params(tk.request.args)
                ),
            },
        )

    def _get_bulk_actions(self, value: str) -> Callable[[list[str]], bool] | None:
        return {"1": self._remove_emails}.get(value)

    def _remove_emails(self, mail_ids: list[str]) -> bool:
        for mail_id in mail_ids:
            try:
                tk.get_action("mc_mail_delete")(
                    {"ignore_auth": True},
                    {"id": mail_id},
                )
            except tk.ObjectNotFound:
                pass

        return True

    def post(self) -> Response:
        if "clear_mails" in tk.request.form:
            tk.get_action("mc_mail_clear")({"ignore_auth": True}, {})
            tk.h.flash_success(tk._("Mails have been cleared."))
            return tk.redirect_to("mailcraft.dashboard")

        bulk_action = tk.request.form.get("bulk-action", "0")
        mail_ids = tk.request.form.getlist("entity_id")

        if not bulk_action or not mail_ids:
            return tk.redirect_to("mailcraft.dashboard")

        action_func = self._get_bulk_actions(bulk_action)

        if not action_func:
            tk.h.flash_error(tk._("The bulk action is not implemented"))
            return tk.redirect_to("mailcraft.dashboard")

        action_func(mail_ids)

        tk.h.flash_success(tk._("Done."))

        return tk.redirect_to("mailcraft.dashboard")


class ConfigView(MethodView):
    def get(self) -> str:
        return tk.render(
            "mailcraft/config.html",
            extra_vars={
                "data": {},
                "errors": {},
                "configs": mc_config.get_config_options(),
            },
        )

    def post(self) -> str:
        data_dict = parse_params(tk.request.form)

        try:
            tk.get_action("config_option_update")(
                {"user": tk.current_user.name},
                data_dict,
            )
        except tk.ValidationError as e:
            return tk.render(
                "mailcraft/config.html",
                extra_vars={
                    "data": data_dict,
                    "errors": e.error_dict,
                    "error_summary": e.error_summary,
                    "configs": mc_config.get_config_options(),
                },
            )

        tk.h.flash_success(tk._("Config options have been updated"))
        return tk.h.redirect_to("mailcraft.config")


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


def send_test_email() -> Response:
    from ckanext.mailcraft.mailer import DefaultMailer

    mailer = DefaultMailer()
    mailer.mail_recipients(
        subject="Hello world",
        recipients=["kvaqich@gmail.com"],
        body="Hello world",
        body_html=tk.render(
            "mailcraft/emails/test.html",
            extra_vars={"site_url": mailer.site_url, "site_title": mailer.site_title},
        ),
    )
    tk.h.flash_success(tk._("Test email has been sent"))

    return tk.redirect_to("mailcraft.dashboard")


mailcraft.add_url_rule("/test", endpoint="test", view_func=send_test_email)
mailcraft.add_url_rule("/config", view_func=ConfigView.as_view("config"))
mailcraft.add_url_rule("/dashboard", view_func=DashboardView.as_view("dashboard"))
mailcraft.add_url_rule(
    "/dashboard/read/<mail_id>", view_func=MailReadView.as_view("mail_read")
)


def get_blueprints():
    return [mailcraft]
