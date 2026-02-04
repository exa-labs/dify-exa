from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

WEBSETS_BASE_URL = "https://api.exa.ai/websets/v0/websets"


class ExaCreateWebsetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        query = tool_parameters.get("query", "")
        if not query:
            raise ValueError("Search query is required")

        count = int(tool_parameters.get("count", 10))
        entity_type = tool_parameters.get("entity_type")
        criteria_str = tool_parameters.get("criteria", "")
        enrichments_str = tool_parameters.get("enrichments", "")
        title = tool_parameters.get("title")

        search: dict[str, Any] = {
            "query": query,
            "count": count,
        }

        if entity_type:
            search["entity"] = {"type": entity_type}

        if criteria_str:
            criteria_lines = [line.strip() for line in criteria_str.strip().split("\n") if line.strip()]
            if criteria_lines:
                search["criteria"] = [{"description": c} for c in criteria_lines[:5]]

        payload: dict[str, Any] = {"search": search}

        if enrichments_str:
            enrichment_lines = [line.strip() for line in enrichments_str.strip().split("\n") if line.strip()]
            if enrichment_lines:
                payload["enrichments"] = [{"description": e, "format": "text"} for e in enrichment_lines]

        if title:
            payload["title"] = title

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "x-exa-integration": "dify",
        }

        response = requests.post(WEBSETS_BASE_URL, json=payload, headers=headers)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_result(result_data))

    def _format_result(self, data: dict) -> str:
        webset_id = data.get("id", "")
        status = data.get("status", "unknown")
        title = data.get("title", "Untitled")

        lines = [
            f"## Webset Created\n",
            f"**ID:** `{webset_id}`",
            f"**Title:** {title}",
            f"**Status:** {status}\n",
        ]

        searches = data.get("searches", [])
        if searches:
            s = searches[0]
            lines.append(f"**Query:** {s.get('query', '')}")
            lines.append(f"**Count:** {s.get('count', '')}")
            progress = s.get("progress", {})
            if progress:
                lines.append(f"**Progress:** {progress.get('completion', 0)}% (found: {progress.get('found', 0)}, analyzed: {progress.get('analyzed', 0)})")

        enrichments = data.get("enrichments", [])
        if enrichments:
            lines.append(f"\n**Enrichments:** {len(enrichments)}")
            for e in enrichments:
                lines.append(f"- {e.get('description', '')}")

        lines.append(f"\nUse **Exa Get Webset** with ID `{webset_id}` to check status and retrieve results.")

        return "\n".join(lines)
