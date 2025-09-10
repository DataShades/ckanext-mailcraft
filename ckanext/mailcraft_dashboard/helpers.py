import json
from typing import Any

import ckan.plugins.toolkit as tk


def mc_dumps(value: Any) -> str:
    """Convert a value to a JSON string.

    Args:
        value: The value to convert to a JSON string

    Returns:
        The JSON string
    """
    return json.dumps(value)


def mc_build_url_from_params(
    endpoint: str, url_params: dict[str, Any], row: dict[str, Any]
) -> str:
    """Build an action URL based on the endpoint and URL parameters.

    The url_params might contain values like $id, $type, etc.
    We need to replace them with the actual values from the row

    Args:
        endpoint: The endpoint to build the URL for
        url_params: The URL parameters to build the URL for
        row: The row to build the URL for
    """
    params = url_params.copy()

    for key, value in params.items():
        if value.startswith("$"):
            params[key] = row[value[1:]]

    return tk.url_for(endpoint, **params)
