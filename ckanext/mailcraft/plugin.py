from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig

import ckanext.mailcraft.config as mc_config
from ckanext.mailcraft.mailer import DefaultMailer


@toolkit.blanket.config_declarations
class MailcraftPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")

    # IConfigurable

    def configure(self, config: CKANConfig) -> None:
        if mc_config.is_startup_conn_test_enabled():
            DefaultMailer().test_conn()
