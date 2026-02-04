from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from tools.exa_search import ExaSearchTool


class ExaProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            tool = ExaSearchTool.from_credentials(credentials)
            for _ in tool.invoke(tool_parameters={"query": "test", "num_results": 1}):
                pass
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
