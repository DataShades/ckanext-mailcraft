from __future__ import annotations

import sqlalchemy as sa
from dominate import tags

import ckan.plugins.toolkit as tk

from ckanext.collection.utils import Filters, ModelData
from ckanext.collection.types import InputFilter, SelectFilter

from ckanext.ap_main.collection.base import (
    ApCollection,
    BulkAction,
    RowAction,
    GlobalAction,
)

from ckanext.mailcraft_dashboard.model import Email


class MailCollection(ApCollection):
    ColumnsFactory = ApCollection.ColumnsFactory.with_attributes(
        names=[
            "bulk-action",
            "id",
            "subject",
            "sender",
            "recipient",
            "state",
            "timestamp",
            "row_actions",
        ],
        sortable={
            "subject",
            "sender",
            "recipient",
            "timestamp",
        },
        width={"bulk-action": "3%", "id": "4%"},
        searchable={"subject"},
        labels={
            "bulk-action": tk.literal(
                tags.input_(
                    type="checkbox",
                    name="bulk_check",
                    id="bulk_check",
                    data_module="ap-bulk-check",
                    data_module_selector='input[name="entity_id"]',
                )
            ),
            "id": "Id",
            "subject": "Subject",
            "sender": "Sender",
            "recipient": "Recipient",
            "state": "State",
            "timestamp": "Timestamp",
            "row_actions": "Actions",
        },
        serializers={
            "id": [("copy_into", {"target": "bulk-action"})],
            "timestamp": [("date", {})],
        },
    )

    DataFactory = ModelData.with_attributes(
        model=Email,
        use_naive_search=True,
        use_naive_filters=True,
        static_columns=[*sa.inspect(Email).columns, Email.id.label("bulk-action")],
    )

    FiltersFactory = Filters.with_attributes(
        static_actions=[
            BulkAction(
                name="bulk-action",
                type="bulk_action",
                options={
                    "label": "Action",
                    "options": [{"value": "1", "text": "Remove selected mails"}],
                },
            ),
            GlobalAction(
                name="clear_mails",
                type="global_action",
                options={
                    "label": "Clear mails",
                    "attrs": {
                        "type": "submit",
                        "class": "btn btn-danger",
                        "data-module": "ap-confirm-action",
                        "data-module-content": (
                            "Are you sure you want to clear all mails?"
                        ),
                        "data-module-with-data": "true",
                    },
                },
            ),
            RowAction(
                name="edit",
                type="row_action",
                options={
                    "endpoint": "mailcraft.mail_read",
                    "label": "View",
                    "params": {"mail_id": "$id"},
                },
            ),
        ],
        static_filters=[
            InputFilter(
                name="q",
                type="input",
                options={
                    "label": "Search",
                    "placeholder": "Search",
                },
            ),
            SelectFilter(
                name="state",
                type="select",
                options={
                    "label": "Level",
                    "options": [
                        {"value": "", "text": "All"},
                        {"value": Email.State.failed, "text": "failed"},
                        {"value": Email.State.stopped, "text": "stopped"},
                        {"value": Email.State.success, "text": "success"},
                    ],
                },
            )
        ],
    )
