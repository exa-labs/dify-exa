from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

WEBSETS_BASE_URL = "https://api.exa.ai/websets/v0/websets"


class ExaGetWebsetTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        webset_id = tool_parameters.get("webset_id", "")
        if not webset_id:
            raise ValueError("Webset ID is required")

        include_items = tool_parameters.get("include_items", True)

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "x-exa-integration": "dify",
        }

        params = {}
        if include_items:
            params["expand"] = "items"

        response = requests.get(f"{WEBSETS_BASE_URL}/{webset_id}", headers=headers, params=params)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_result(result_data))

    def _format_result(self, data: dict) -> str:
        webset_id = data.get("id", "")
        status = data.get("status", "unknown")
        title = data.get("title", "Untitled")

        lines = [
            f"## Webset: {title}\n",
            f"**ID:** `{webset_id}`",
            f"**Status:** {status}\n",
        ]

        searches = data.get("searches", [])
        if searches:
            s = searches[0]
            lines.append(f"**Query:** {s.get('query', '')}")
            progress = s.get("progress", {})
            if progress:
                lines.append(f"**Progress:** {progress.get('completion', 0)}% (found: {progress.get('found', 0)}, analyzed: {progress.get('analyzed', 0)})")
            lines.append("")

        items = data.get("items", [])
        if items:
            lines.append(f"### Items ({len(items)})\n")
            for i, item in enumerate(items, 1):
                item_title = item.get("title", "Untitled")
                url = item.get("url", "")
                lines.append(f"**{i}. [{item_title}]({url})**")

                enrichment_results = item.get("enrichments", {})
                if enrichment_results:
                    for key, val in enrichment_results.items():
                        if isinstance(val, dict):
                            value = val.get("value", "")
                            if value:
                                lines.append(f"  - {key}: {value}")
                        else:
                            lines.append(f"  - {key}: {val}")

                lines.append("")
        elif status in ("idle", "running", "pending"):
            lines.append("*Webset is still processing. Check back later.*")

        return "\n".join(lines)
