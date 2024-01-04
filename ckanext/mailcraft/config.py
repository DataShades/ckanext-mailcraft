from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk
from ckan import types

CONF_TEST_CONN = "ckanext.mailcraft.test_conn_on_startup"
DEF_TEST_CONN = False

CONF_CONN_TIMEOUT = "ckanext.mailcraft.conn_timeout"
DEF_CONN_TIMEOUT = 10

CONF_STOP_OUTGOING = "ckanext.mailcraft.stop_outgoing_emails"
DEF_STOP_OUTGOING = False

CONF_MAIL_PER_PAGE = "ckanext.mailcraft.mail_per_page"
DEF_MAIL_PER_PAGE = 20

CONF_REDIRECT_EMAILS_TO = "ckanext.mailcraft.redirect_emails_to"


def get_conn_timeout() -> int:
    """Return a timeout for an SMTP connection"""
    return tk.asint(tk.config.get(CONF_CONN_TIMEOUT) or DEF_CONN_TIMEOUT)


def is_startup_conn_test_enabled() -> bool:
    """Check do we want to check an SMTP conn on CKAN startup"""

    return tk.asbool(tk.config.get(CONF_TEST_CONN, DEF_TEST_CONN))


def stop_outgoing_emails() -> bool:
    """Check if we are stopping outgoing emails. In this case, we are only
    saving it to dashboard"""
    return tk.asbool(tk.config.get(CONF_STOP_OUTGOING, DEF_STOP_OUTGOING))


def get_mail_per_page() -> int:
    """Return a number of mails to show per page"""
    return tk.asint(tk.config.get(CONF_MAIL_PER_PAGE) or DEF_MAIL_PER_PAGE)


def get_redirect_email() -> str | None:
    """Redirect outgoing emails to a specified email"""
    return tk.config.get(CONF_REDIRECT_EMAILS_TO)


def get_config_options() -> dict[str, dict[str, Any]]:
    """Defines how we are going to render the global configuration
    options for an extension."""
    unicode_safe = tk.get_validator("unicode_safe")
    boolean_validator = tk.get_validator("boolean_validator")
    default = tk.get_validator("default")
    int_validator = tk.get_validator("is_positive_integer")
    email_validator = tk.get_validator("email_validator")

    return {
        "smtp_test": {
            "key": CONF_TEST_CONN,
            "label": "Test SMTP connection on CKAN startup",
            "value": is_startup_conn_test_enabled(),
            "validators": [default(DEF_TEST_CONN), boolean_validator],  # type: ignore
            "type": "select",
            "options": [{"value": 1, "text": "Yes"}, {"value": 0, "text": "No"}],
        },
        "timeout": {
            "key": CONF_CONN_TIMEOUT,
            "label": "SMTP connection timeout",
            "value": get_conn_timeout(),
            "validators": [default(DEF_CONN_TIMEOUT), int_validator],  # type: ignore
            "type": "number",
        },
        "stop_outgoing": {
            "key": CONF_STOP_OUTGOING,
            "label": "Stop outgoing emails",
            "value": stop_outgoing_emails(),
            "validators": [default(DEF_STOP_OUTGOING), boolean_validator],  # type: ignore
            "type": "select",
            "options": [{"value": 1, "text": "Yes"}, {"value": 0, "text": "No"}],
        },
        "mail_per_page": {
            "key": CONF_MAIL_PER_PAGE,
            "label": "Number of emails per page",
            "value": get_mail_per_page(),
            "validators": [default(DEF_MAIL_PER_PAGE), int_validator],  # type: ignore
            "type": "number",
        },
        "redirect_to": {
            "key": CONF_REDIRECT_EMAILS_TO,
            "label": "Redirect outgoing emails to",
            "value": get_redirect_email(),
            "validators": [unicode_safe, email_validator],
            "type": "text",
        },
    }
