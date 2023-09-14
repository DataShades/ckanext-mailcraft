from __future__ import annotations

from typing import Any, Dict

from ckan.logic.schema import validator_args


Schema = Dict[str, Any]


@validator_args
def mail_list_schema() -> Schema:
    return {}


@validator_args
def mail_show_schema(not_empty, unicode_safe, mc_mail_exists) -> Schema:
    return {"id": [not_empty, unicode_safe, mc_mail_exists]}


@validator_args
def mail_delete_schema(not_empty, unicode_safe, mc_mail_exists) -> Schema:
    return {"id": [not_empty, unicode_safe, mc_mail_exists]}
