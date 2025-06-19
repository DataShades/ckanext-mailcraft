from __future__ import annotations

import ckan.types as types
from ckan.logic.schema import validator_args
from ckanext.mailcraft_dashboard.model import Email


@validator_args
def mail_create_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    default: types.Validator,
    json_object: types.Validator,
    ignore_missing: types.Validator,
    ignore: types.Validator,
) -> types.Schema:
    return {
        "subject": [not_empty, unicode_safe],
        "sender": [not_empty, unicode_safe],
        "recipient": [not_empty, unicode_safe],
        "message": [not_empty, unicode_safe],
        "state": [default(Email.State.success), unicode_safe],  # type: ignore
        "extras": [ignore_missing, json_object],
        "__extras": [ignore],
    }


@validator_args
def mail_list_schema() -> types.Schema:
    return {}


@validator_args
def mail_show_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    mc_mail_exists: types.Validator,
) -> types.Schema:
    return {"id": [not_empty, unicode_safe, mc_mail_exists]}


@validator_args
def mail_delete_schema(
    not_empty: types.Validator,
    unicode_safe: types.Validator,
    mc_mail_exists: types.Validator,
) -> types.Schema:
    return {"id": [not_empty, unicode_safe, mc_mail_exists]}
