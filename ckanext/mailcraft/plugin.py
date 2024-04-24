from __future__ import annotations

import ckan.types as types
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import CKANConfig

import ckanext.mailcraft.config as mc_config
from ckanext.mailcraft.mailer import DefaultMailer
from ckanext.mailcraft.collection import MailCollection


@toolkit.blanket.blueprints
@toolkit.blanket.actions
@toolkit.blanket.auth_functions
@toolkit.blanket.validators
@toolkit.blanket.config_declarations
class MailcraftPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IConfigurable)
    plugins.implements(plugins.ISignal)

    try:
        from ckanext.collection.interfaces import ICollection, CollectionFactory
    except ImportError:
        pass
    else:
        plugins.implements(ICollection, inherit=True)

        # ICollection

        def get_collection_factories(self) -> dict[str, CollectionFactory]:
            return {
                "mailcraft-dashboard": MailCollection,
            }

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

    # ISignal

    def get_signal_subscriptions(self) -> types.SignalMapping:
        return {
            toolkit.signals.ckanext.signal("ap_main:collect_config_sections"): [
                self.collect_config_sections_subs
            ],
            toolkit.signals.ckanext.signal("ap_main:collect_config_schemas"): [
                self.collect_config_schemas_subs
            ],
        }

    @staticmethod
    def collect_config_sections_subs(sender: None):
        return {
            "name": "Mailcraft",
            "configs": [
                {
                    "name": "Global settings",
                    "blueprint": "mailcraft.config",
                    "info": "Global mailcraft configurations",
                },
                {
                    "name": "Dashboard",
                    "blueprint": "mailcraft.dashboard",
                    "info": "Mailcraft dashboard",
                },
            ],
        }

    @staticmethod
    def collect_config_schemas_subs(sender: None):
        return ["ckanext.mailcraft:config_schema.yaml"]
