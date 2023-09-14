import ckan.plugins.toolkit as tk


CONF_TEST_CONN = "ckanext.mailcraft.test_conn_on_startup"
DEF_TEST_CONN = False

CONF_CONN_TIMEOUT = "ckanext.mailcraft.conn_timeout"
DEF_CONN_TIMEOUT = 10


def get_conn_timeout() -> int:
    """Return a timeout for an SMTP connection"""
    return tk.asint(tk.config.get(CONF_CONN_TIMEOUT, DEF_CONN_TIMEOUT))


def is_startup_conn_test_enabled() -> bool:
    """Check do we want to check an SMTP conn on CKAN startup"""

    return tk.asbool(tk.config.get(CONF_TEST_CONN, DEF_TEST_CONN))
