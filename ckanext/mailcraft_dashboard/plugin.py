from __future__ import annotations

import ckan.plugins as p
import ckan.plugins.toolkit as tk
from ckan.common import CKANConfig


@tk.blanket.blueprints
@tk.blanket.actions
@tk.blanket.auth_functions
@tk.blanket.validators
class MailcraftDashboardPlugin(p.SingletonPlugin):
    p.implements(p.IConfigurer)

    # IConfigurer

    def update_config(self, config_: CKANConfig):
        tk.add_template_directory(config_, "templates")
