from __future__ import annotations

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


@toolkit.blanket.blueprints
@toolkit.blanket.actions
@toolkit.blanket.auth_functions
@toolkit.blanket.validators
@toolkit.blanket.helpers
class MailcraftDashboardPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_resource("assets", "mailcraft_dashboard")
        toolkit.add_template_directory(config_, "templates")
