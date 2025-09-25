from __future__ import annotations

from sqlalchemy import select

import ckan.plugins.toolkit as tk
from ckan.types import Context

from ckanext.tables.shared import (
    ActionDefinition,
    ColumnDefinition,
    DatabaseDataSource,
    GlobalActionDefinition,
    GlobalActionHandlerResult,
    Row,
    TableDefinition,
    formatters,
)

from ckanext.mailcraft_dashboard.model import Email


class DashboardTable(TableDefinition):
    """Table definition for the mailcraft dashboard."""

    def __init__(self):
        """Initialize the table definition."""
        super().__init__(
            name="mailcraft",
            data_source=DatabaseDataSource(
                stmt=select(
                    Email.id,
                    Email.subject,
                    Email.sender,
                    Email.recipient,
                    Email.state,
                    Email.timestamp,
                ).order_by(Email.timestamp.desc()),
                model=Email,
            ),
            columns=[
                ColumnDefinition(
                    field="id", filterable=False, resizable=False, width=60
                ),
                ColumnDefinition(field="subject", width=250),
                ColumnDefinition(field="sender"),
                ColumnDefinition(field="recipient"),
                ColumnDefinition(field="state", resizable=False, width=100),
                ColumnDefinition(
                    field="timestamp",
                    formatters=[
                        (formatters.DateFormatter, {"date_format": "%Y-%m-%d %H:%M"}),
                        (formatters.TextBoldFormatter, {})
                    ],
                    tabulator_formatter="html",
                    resizable=False,
                    width=150,
                ),
                ColumnDefinition(
                    field="actions",
                    formatters=[(formatters.ActionsFormatter, {})],
                    filterable=False,
                    tabulator_formatter="html",
                    sortable=False,
                    resizable=False,
                    width=100,
                ),
            ],
            actions=[
                ActionDefinition(
                    name="view",
                    label=tk._("View"),
                    icon="fa fa-eye",
                    endpoint="mailcraft.mail_read",
                    url_params={
                        "view": "read",
                        "mail_id": "$id",
                    },
                ),
            ],
            global_actions=[
                GlobalActionDefinition(
                    action="delete",
                    label=tk._("Delete selected entities"),
                    callback=self.ga_remove_emails,
                ),
            ],
            table_action_snippet="mailcraft/table_actions.html",
        )

    @staticmethod
    def ga_remove_emails(row: Row) -> GlobalActionHandlerResult:
        try:
            tk.get_action("mc_mail_delete")(
                {"ignore_auth": True},
                {"id": row["id"]},
            )
        except tk.ObjectNotFound:
            return False, tk._("Mail not found")

        return True, None

    @classmethod
    def check_access(cls, context: Context) -> None:
        tk.check_access("sysadmin", context)
