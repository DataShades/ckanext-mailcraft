import ckan.plugins.toolkit as tk

from ckanext.tables.shared import FormatterResult, Options, Value, formatters


class StatusFormatter(formatters.BaseFormatter):
    """Formatter for the status column."""

    def format(self, value: Value, options: Options) -> FormatterResult:
        """Format the status value."""
        state_map = {"success": "success", "failed": "danger", "stopped": "black"}

        label_type = state_map.get(value, "black")

        return tk.literal(
            f'<span class="text-uppercase px-2 py-1 badge bg-{label_type}">{value}</span>'
        )
