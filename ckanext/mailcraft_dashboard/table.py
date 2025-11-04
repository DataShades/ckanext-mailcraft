from __future__ import annotations

from sqlalchemy import select

import ckan.plugins.toolkit as tk
from ckan.types import Context

from ckanext.tables.shared import (
    ActionHandlerResult,
    BulkActionDefinition,
    BulkActionHandlerResult,
    ColumnDefinition,
    DatabaseDataSource,
    Row,
    RowActionDefinition,
    TableActionDefinition,
    TableDefinition,
    exporters,
    formatters,
)

from ckanext.mailcraft.utils import get_mailer
from ckanext.mailcraft_dashboard.formatters import StatusFormatter
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
                ColumnDefinition(field="subject", width=250),
                ColumnDefinition(field="sender"),
                ColumnDefinition(field="recipient"),
                ColumnDefinition(
                    field="state",
                    resizable=False,
                    width=100,
                    tabulator_formatter="html",
                    formatters=[(StatusFormatter, {})],
                ),
                ColumnDefinition(
                    field="timestamp",
                    formatters=[
                        (
                            formatters.DateFormatter,
                            {"date_format": "%Y-%m-%dT%H:%M:%S"},
                        ),
                    ],
                    tabulator_formatter="html",
                    resizable=False,
                    width=170,
                ),
            ],
            row_actions=[
                RowActionDefinition(
                    action="view",
                    label=tk._("View"),
                    icon="fa fa-eye",
                    callback=self.row_action_view,
                ),
                RowActionDefinition(
                    action="delete",
                    label=tk._("Delete"),
                    icon="fa fa-trash",
                    callback=self.row_action_delete,
                    with_confirmation=True,
                ),
            ],
            bulk_actions=[
                BulkActionDefinition(
                    action="delete",
                    label=tk._("Delete selected entities"),
                    icon="fa fa-trash",
                    callback=self.bulk_action_remove_emails,
                )
            ],
            table_actions=[
                TableActionDefinition(
                    action="clear_emails",
                    label=tk._("Clear mails"),
                    icon="fa fa-trash",
                    callback=self.table_action_clear_emails,
                ),
                TableActionDefinition(
                    action="send_test_mail",
                    label=tk._("Send test mail"),
                    icon="fa fa-paper-plane",
                    callback=self.table_action_send_test_mail,
                ),
            ],
            exporters=[
                exporters.CSVExporter,
                exporters.JSONExporter,
                exporters.XLSXExporter,
                exporters.YAMLExporter,
                exporters.TSVExporter,
                exporters.NDJSONExporter,
                exporters.HTMLExporter,
            ],
        )

    @staticmethod
    def row_action_view(row: Row) -> ActionHandlerResult:
        return ActionHandlerResult(
            success=True,
            error=None,
            redirect=tk.h.url_for("mailcraft.mail_read", mail_id=row["id"]),
        )

    @staticmethod
    def row_action_delete(row: Row) -> ActionHandlerResult:
        try:
            tk.get_action("mc_mail_delete")(
                {"ignore_auth": True},
                {"id": row["id"]},
            )
        except tk.ObjectNotFound:
            return ActionHandlerResult(success=False, error=tk._("Mail not found"))

        return ActionHandlerResult(success=True, error=None)

    @staticmethod
    def bulk_action_remove_emails(row: Row) -> BulkActionHandlerResult:
        try:
            tk.get_action("mc_mail_delete")(
                {"ignore_auth": True},
                {"id": row["id"]},
            )
        except tk.ObjectNotFound:
            return BulkActionHandlerResult(success=False, error=tk._("Mail not found"))

        return BulkActionHandlerResult(success=True, error=None)

    def table_action_clear_emails(self) -> ActionHandlerResult:
        try:
            tk.get_action("mc_mail_clear")({"ignore_auth": True}, {})
        except tk.ValidationError as e:
            return ActionHandlerResult(success=False, error=str(e))

        return ActionHandlerResult(success=True, error=None)

    def table_action_send_test_mail(self) -> ActionHandlerResult:
        """Send a test email and redirect to the dashboard."""
        mailer = get_mailer()

        result = mailer.mail_recipients(
            subject="Hello world",
            recipients=["test@gmail.com"],
            body="Hello world",
            body_html=tk.render(
                "mailcraft/emails/test.html",
                extra_vars={
                    "site_url": mailer.site_url,
                    "site_title": mailer.site_title,
                },
            ),
        )

        if not result:
            return ActionHandlerResult(
                success=False,
                error=tk._("Failed to send test email. Check your mail settings."),
            )

        return ActionHandlerResult(success=True, error=None)

    @classmethod
    def check_access(cls, context: Context) -> None:
        tk.check_access("sysadmin", context)
