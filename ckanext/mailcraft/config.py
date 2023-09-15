import ckan.plugins.toolkit as tk

CONF_TEST_CONN = "ckanext.mailcraft.test_conn_on_startup"
DEF_TEST_CONN = False

CONF_CONN_TIMEOUT = "ckanext.mailcraft.conn_timeout"
DEF_CONN_TIMEOUT = 10

CONF_STOP_OUTGOING = "ckanext.mailcraft.stop_outgoing_emails"
DEF_STOP_OUTGOING = False

CONF_MAIL_PER_PAGE = "ckanext.mailcraft.mail_per_page"
DEF_MAIL_PER_PAGE = 20

CONF_SAVE_TO_DASHBOARD = "ckanext.mailcraft.save_to_dashboard"
DEF_SAVE_TO_DASHBOARD = False


def get_conn_timeout() -> int:
    """Return a timeout for an SMTP connection"""
    return tk.asint(tk.config.get(CONF_CONN_TIMEOUT, DEF_CONN_TIMEOUT))


def is_startup_conn_test_enabled() -> bool:
    """Check do we want to check an SMTP conn on CKAN startup"""

    return tk.asbool(tk.config.get(CONF_TEST_CONN, DEF_TEST_CONN))


def stop_outgoing_emails() -> bool:
    """Check if we are stopping outgoing emails. In this case, we are only
    saving it to dashboard"""
    return tk.asbool(tk.config.get(CONF_STOP_OUTGOING, DEF_STOP_OUTGOING))


def get_mail_per_page() -> int:
    """Return a number of mails to show per page"""
    return tk.asint(tk.config.get(CONF_MAIL_PER_PAGE, DEF_MAIL_PER_PAGE))


def is_save_to_dashboard_enabled() -> bool:
    """Check if we are saving outgoing emails to dashboard"""
    return tk.asbool(tk.config.get(CONF_SAVE_TO_DASHBOARD, DEF_SAVE_TO_DASHBOARD))
