from __future__ import annotations

import ckan.plugins.toolkit as tk

CONF_TEST_CONN = "ckanext.mailcraft.test_conn_on_startup"
DEF_TEST_CONN = False

CONF_CONN_TIMEOUT = "ckanext.mailcraft.conn_timeout"
DEF_CONN_TIMEOUT = 10

CONF_STOP_OUTGOING = "ckanext.mailcraft.stop_outgoing_emails"
DEF_STOP_OUTGOING = False

CONF_SAVE_EMAILS_TO_DB = "ckanext.mailcraft.save_emails"
DEF_SAVE_EMAILS_TO_DB = False

CONF_MAIL_PER_PAGE = "ckanext.mailcraft.mail_per_page"
DEF_MAIL_PER_PAGE = 20

CONF_REDIRECT_EMAILS_TO = "ckanext.mailcraft.redirect_emails_to"

CONF_STORE_ATTACHMENTS = "ckanext.mailcraft.store_attachment_content"
DEF_STORE_ATTACHMENTS = False


def get_conn_timeout() -> int:
    """Return a timeout for an SMTP connection."""
    return tk.asint(tk.config.get(CONF_CONN_TIMEOUT) or DEF_CONN_TIMEOUT)


def is_startup_conn_test_enabled() -> bool:
    """Check do we want to check an SMTP conn on CKAN startup."""
    return tk.asbool(tk.config.get(CONF_TEST_CONN, DEF_TEST_CONN))


def stop_outgoing_emails() -> bool:
    """Check if we are stopping outgoing emails.

    In this case, we are only, we are only saving it to dashboard
    """
    return tk.asbool(tk.config.get(CONF_STOP_OUTGOING, DEF_STOP_OUTGOING))


def save_emails_to_db() -> bool:
    """Check if we are saving emails to database."""
    return tk.asbool(tk.config.get(CONF_SAVE_EMAILS_TO_DB, DEF_SAVE_EMAILS_TO_DB))


def get_mail_per_page() -> int:
    """Return a number of mails to show per page."""
    return tk.asint(tk.config.get(CONF_MAIL_PER_PAGE) or DEF_MAIL_PER_PAGE)


def get_redirect_email() -> list[str]:
    """Redirect outgoing emails to a specified email."""
    return tk.config.get(CONF_REDIRECT_EMAILS_TO, [])


def store_attachments_content() -> bool:
    """Check if we are storing attachments content in the database."""
    return tk.asbool(tk.config.get(CONF_STORE_ATTACHMENTS, DEF_STORE_ATTACHMENTS))
