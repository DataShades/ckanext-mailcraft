from __future__ import annotations

from typing import Union

from flask import Blueprint

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig

import ckanext.mailcraft.config as mc_config
from ckanext.mailcraft.mailer import DefaultMailer


@toolkit.blanket.actions
@toolkit.blanket.auth_functions
@toolkit.blanket.validators
class MailcraftPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)

    if plugins.plugin_loaded("admin_panel"):
        import ckanext.admin_panel.types as ap_types
        from ckanext.admin_panel.interfaces import IAdminPanel

        plugins.implements(plugins.IBlueprint)
        plugins.implements(IAdminPanel, inherit=True)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, "templates")
        toolkit.add_public_directory(config_, "public")
        toolkit.add_resource("assets", "mailcraft")

    # IConfigurable

    def configure(self, config: CKANConfig) -> None:
        if mc_config.is_startup_conn_test_enabled():
            mailer = DefaultMailer()
            mailer.test_conn()

    # IBlueprint

    def get_blueprint(self) -> Union[list[Blueprint], Blueprint]:
        from ckanext.mailcraft.views import get_blueprints

        return get_blueprints()

    # IAdminPanel

    def register_config_sections(
        self, config_list: list[ap_types.SectionConfig]
    ) -> list[ap_types.SectionConfig]:
        config_list.append(
            ap_types.SectionConfig(
                name="Mailcraft",
                configs=[
                    ap_types.ConfigurationItem(
                        name="Global settings",
                        blueprint="mailcraft.config",
                        info="Global mailcraft configurations",
                    ),
                    ap_types.ConfigurationItem(
                        name="Dashboard",
                        blueprint="mailcraft.dashboard",
                        info="Mailcraft dashboard",
                    ),
                ],
            )
        )
        return config_list
