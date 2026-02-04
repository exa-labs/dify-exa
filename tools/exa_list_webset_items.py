from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

WEBSETS_BASE_URL = "https://api.exa.ai/websets/v0/websets"


class ExaListWebsetItemsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        webset_id = tool_parameters.get("webset_id", "")
        if not webset_id:
            raise ValueError("Webset ID is required")

        cursor = tool_parameters.get("cursor")
        limit = int(tool_parameters.get("limit", 25))

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
            "x-exa-integration": "dify",
        }

        params: dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor

        response = requests.get(f"{WEBSETS_BASE_URL}/{webset_id}/items", headers=headers, params=params)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_result(result_data))

    def _format_result(self, data: dict) -> str:
        items = data.get("data", [])
        has_more = data.get("hasMore", False)
        next_cursor = data.get("nextCursor")

        lines = [f"## Webset Items\n", f"**Items on this page:** {len(items)}"]
        if has_more:
            lines.append(f"**More available:** Yes (cursor: `{next_cursor}`)")
        lines.append("")

        for i, item in enumerate(items, 1):
            title = item.get("title", "Untitled")
            url = item.get("url", "")
            lines.append(f"### {i}. [{title}]({url})\n")

            enrichment_results = item.get("enrichments", {})
            if enrichment_results:
                for key, val in enrichment_results.items():
                    if isinstance(val, dict):
                        value = val.get("value", "")
                        if value:
                            lines.append(f"- **{key}:** {value}")
                    else:
                        lines.append(f"- **{key}:** {val}")

            lines.append("---\n")

        return "\n".join(lines)
