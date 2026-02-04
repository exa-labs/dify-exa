from collections.abc import Generator
from typing import Any

import requests

from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ExaFindSimilarTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        api_key = self.runtime.credentials["exa_api_key"]
        url = tool_parameters.get("url", "")
        if not url:
            raise ValueError("URL is required")

        num_results = int(tool_parameters.get("num_results", 10))
        text = tool_parameters.get("text", False)
        highlights = tool_parameters.get("highlights", False)
        summary = tool_parameters.get("summary", False)
        include_domains = tool_parameters.get("include_domains", "")
        exclude_domains = tool_parameters.get("exclude_domains", "")
        start_published_date = tool_parameters.get("start_published_date", "")
        end_published_date = tool_parameters.get("end_published_date", "")
        include_text = tool_parameters.get("include_text")
        exclude_text = tool_parameters.get("exclude_text")
        category = tool_parameters.get("category")

        include_domains_list = [d.strip() for d in include_domains.split(",") if d.strip()] if include_domains else []
        exclude_domains_list = [d.strip() for d in exclude_domains.split(",") if d.strip()] if exclude_domains else []

        payload: dict[str, Any] = {
            "url": url,
            "numResults": num_results,
        }

        if include_domains_list:
            payload["includeDomains"] = include_domains_list
        if exclude_domains_list:
            payload["excludeDomains"] = exclude_domains_list
        if start_published_date:
            payload["startPublishedDate"] = start_published_date
        if end_published_date:
            payload["endPublishedDate"] = end_published_date
        if include_text:
            payload["includeText"] = [include_text]
        if exclude_text:
            payload["excludeText"] = [exclude_text]
        if category:
            payload["category"] = category

        contents: dict[str, Any] = {}
        if text:
            contents["text"] = True
        if highlights:
            contents["highlights"] = True
        if summary:
            contents["summary"] = True
        if contents:
            payload["contents"] = contents

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

        response = requests.post("https://api.exa.ai/findSimilar", json=payload, headers=headers)
        response.raise_for_status()
        result_data = response.json()

        yield self.create_json_message(result_data)
        yield self.create_text_message(self._format_results(result_data, url))

    def _format_results(self, data: dict, source_url: str) -> str:
        results = data.get("results", [])
        lines = [f"## Exa Similar Results\n", f"**Similar to:** {source_url}\n", f"**Results:** {len(results)}\n"]

        for i, r in enumerate(results, 1):
            title = r.get("title", "Untitled")
            url = r.get("url", "")
            lines.append(f"### {i}. [{title}]({url})\n")

            if r.get("publishedDate"):
                lines.append(f"**Published:** {r['publishedDate']}")
            if "score" in r:
                lines.append(f"**Score:** {r['score']:.4f}")

            if r.get("summary"):
                lines.append(f"\n**Summary:** {r['summary']}\n")

            if r.get("highlights"):
                lines.append("\n**Highlights:**")
                for h in r["highlights"]:
                    lines.append(f"> {h}")

            if r.get("text"):
                text = r["text"][:500] + "..." if len(r.get("text", "")) > 500 else r.get("text", "")
                lines.append(f"\n```\n{text}\n```")

            lines.append("---\n")

        return "\n".join(lines)
