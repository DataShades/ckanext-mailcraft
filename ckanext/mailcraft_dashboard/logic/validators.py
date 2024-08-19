from __future__ import annotations

from typing import Any

import ckan.plugins.toolkit as tk

import ckanext.mailcraft_dashboard.model as mc_model


def mc_mail_exists(v: str, context) -> Any:
    """Ensures that the mail with a given id exists"""

    result = mc_model.Email.get(v)

    if not result:
        raise tk.Invalid(f"The ьфшд with an id {v} doesn't exist.")

    return v
