import ckan.plugins.toolkit as tk

CONF_TEST_CONN = "ckanext.mailcraft.test_conn_on_startup"
DEF_TEST_CONN = False

CONF_CONN_TIMEOUT = "ckanext.mailcraft.conn_timeout"
DEF_CONN_TIMEOUT = 10

CONF_STOP_OUTGOING = "ckanext.mailcraft.stop_outgoing_emails"
DEF_STOP_OUTGOING = False


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
