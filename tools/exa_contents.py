from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExaContentsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        urls_str = tool_parameters.get("urls", "")
        if not urls_str:
            raise ValueError("At least one URL is required")

        urls = [u.strip() for u in urls_str.split(",") if u.strip()]
        if not urls:
            raise ValueError("At least one valid URL is required")

        text = tool_parameters.get("text", True)
        highlights = tool_parameters.get("highlights", False)
        summary = tool_parameters.get("summary", False)
        livecrawl = tool_parameters.get("livecrawl", "never")
        subpages = tool_parameters.get("subpages")

        payload: dict[str, Any] = {
            "ids": urls,
        }

        contents: dict[str, Any] = {}
        if text:
            contents["text"] = True
        if highlights:
            contents["highlights"] = True
        if summary:
            contents["summary"] = True
        if contents:
            payload["contents"] = contents

        if livecrawl and livecrawl != "never":
            payload["livecrawl"] = livecrawl
        if subpages is not None:
            payload["subpages"] = int(subpages)

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

        response = requests.post("https://api.exa.ai/contents", json=payload, headers=headers)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_results(result_data))

    def _format_results(self, data: dict) -> str:
        results = data.get("results", [])
        lines = [f"## Exa Contents\n", f"**Pages Retrieved:** {len(results)}\n"]

        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            lines.append(f"### {i}. [{title}]({url})\n")

            if r.get("summary"):
                lines.append(f"**Summary:** {r['summary']}\n")

            if r.get("highlights"):
                lines.append("**Highlights:**")
                for h in r["highlights"]:
                    lines.append(f"> {h}")
                lines.append("")

            if r.get("text"):
                text = r["text"][:1000] + "..." if len(r.get("text", "")) > 1000 else r.get("text", "")
                lines.append(f"```\n{text}\n```")

            lines.append("---\n")

        return "\n".join(lines)
