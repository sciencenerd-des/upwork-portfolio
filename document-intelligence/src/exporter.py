"""Export helpers for JSON, CSV, and Excel formats."""

from __future__ import annotations

import csv
import io
import json
from typing import Any

from openpyxl import Workbook


def export_json(payload: dict[str, Any]) -> bytes:
    return json.dumps(payload, indent=2).encode("utf-8")


def export_csv(entities: dict[str, list[dict[str, Any]]]) -> bytes:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(["entity_type", "value", "label", "confidence"])

    for entity_type, values in entities.items():
        for item in values:
            writer.writerow(
                [
                    entity_type,
                    item.get("value", ""),
                    item.get("label", ""),
                    item.get("confidence", ""),
                ]
            )

    return buffer.getvalue().encode("utf-8")


def export_excel(
    filename: str,
    summary: str,
    key_points: list[str],
    entities: dict[str, list[dict[str, Any]]],
) -> bytes:
    workbook = Workbook()
    ws_summary = workbook.active
    ws_summary.title = "Summary"

    ws_summary.append(["Document", filename])
    ws_summary.append(["Summary", summary])
    ws_summary.append([])
    ws_summary.append(["Key Points"])
    for point in key_points:
        ws_summary.append([point])

    ws_entities = workbook.create_sheet("Entities")
    ws_entities.append(["Type", "Value", "Label", "Confidence"])
    for entity_type, values in entities.items():
        for item in values:
            ws_entities.append(
                [
                    entity_type,
                    item.get("value", ""),
                    item.get("label", ""),
                    item.get("confidence", ""),
                ]
            )

    data = io.BytesIO()
    workbook.save(data)
    data.seek(0)
    return data.getvalue()
