"""
LangGraph tool: fill_form
Extracts structured HCP form field values from a natural-language message and
returns them as a JSON-serialisable list of {field, value} dicts.
"""
import json
from typing import Any

from langchain_core.tools import tool

from app.schemas.form import FormData

# All valid field names on the frontend form
VALID_FIELDS: set[str] = set(FormData.model_fields.keys())


@tool
def fill_form(field_updates_json: str) -> str:
    """
    Populate one or more HCP form fields from a JSON string.

    Args:
        field_updates_json: A JSON-encoded list of objects, each with
            'field' (str) and 'value' (str) keys.
            Example: '[{"field": "name", "value": "Dr. Smith"}, ...]'

    Returns:
        A JSON string confirming which fields were updated.

    Raises:
        ValueError: If the JSON is malformed or contains unknown field names.
    """
    try:
        updates: list[dict[str, Any]] = json.loads(field_updates_json)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON provided to fill_form: {exc}") from exc

    if not isinstance(updates, list):
        raise ValueError("fill_form expects a JSON array of {field, value} objects.")

    validated: list[dict[str, str]] = []
    for item in updates:
        field = item.get("field", "")
        value = item.get("value", "")
        if field not in VALID_FIELDS:
            raise ValueError(
                f"Unknown field '{field}'. Valid fields: {sorted(VALID_FIELDS)}"
            )
        validated.append({"field": field, "value": str(value)})

    return json.dumps({"status": "ok", "updates": validated})
