"""
QCC MCP Client - V2 融合增强版
基于 Manus 版本 + V1 健壮性增强
"""
import requests
import json
import os
import re
from typing import Dict, List, Optional, Any


class QccMcpClient:
    """企查查 MCP 客户端 - V2 增强版"""

    def __init__(self, mcp_config_path: str = "./.mcp.json"):
        self.mcp_servers = self._load_mcp_config(mcp_config_path)
        self.session = requests.Session()
        self.session.timeout = 30

    def _load_mcp_config(self, mcp_config_path: str) -> Dict:
        """加载 MCP 配置 - V2 增强：多路径查找 + 环境变量回退"""
        config_paths = [
            mcp_config_path,
            os.path.expanduser("~/.claude/.mcp.json"),
            "./.mcp.json",
            "../.mcp.json"
        ]

        for path in config_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if "mcpServers" in config:
                            # 替换环境变量
                            return self._resolve_env_vars(config["mcpServers"])
                except Exception as e:
                    print(f"[QccMcpClient] Warning: Failed to load {path}: {e}")
                    continue

        # V2 增强：环境变量回退
        print("[QccMcpClient] Warning: .mcp.json not found. Using environment variables fallback.")
        return self._load_from_env()

    def _resolve_env_vars(self, servers: Dict) -> Dict:
        """解析配置中的环境变量 - 支持 ${VAR} 和 $VAR 格式"""
        resolved = {}
        env_var_pattern = re.compile(r'\$\{(\w+)\}|\$(\w+)')

        for server_id, config in servers.items():
            resolved[server_id] = {}
            for key, value in config.items():
                if isinstance(value, str):
                    # 替换 ${VAR} 和 $VAR 格式的环境变量
                    def replace_env_var(match):
                        var_name = match.group(1) or match.group(2)
                        return os.getenv(var_name, match.group(0))
                    resolved[server_id][key] = env_var_pattern.sub(replace_env_var, value)
                elif isinstance(value, dict):
                    resolved[server_id][key] = {
                        k: (env_var_pattern.sub(replace_env_var, v) if isinstance(v, str) else v)
                        for k, v in value.items()
                    }
                else:
                    resolved[server_id][key] = value
        return resolved

    def _load_from_env(self) -> Dict:
        """V2 新增：从环境变量加载配置（统一API Key方式）"""
        api_key = os.getenv("QCC_MCP_API_KEY")
        if not api_key:
            print("[QccMcpClient] Error: QCC_MCP_API_KEY environment variable not set.")
            return {}

        # V2 增强：支持4-server配置
        return {
            "qcc-company": {
                "url": "https://agent.qcc.com/mcp/company/stream",
                "headers": {"Authorization": f"Bearer {api_key}"}
            },
            "qcc-risk": {
                "url": "https://agent.qcc.com/mcp/risk/stream",
                "headers": {"Authorization": f"Bearer {api_key}"}
            },
            "qcc-ipr": {
                "url": "https://agent.qcc.com/mcp/ipr/stream",
                "headers": {"Authorization": f"Bearer {api_key}"}
            },
            "qcc-operation": {
                "url": "https://agent.qcc.com/mcp/operation/stream",
                "headers": {"Authorization": f"Bearer {api_key}"}
            }
        }

    def call_mcp_service(self, server_id: str, query: str,
                         api_key: str = None, retry: int = 2) -> Dict:
        """
        调用 MCP 服务 - V2 增强：添加重试机制
        :param server_id: MCP Server ID (qcc-company/risk/ipr/operation 或具体工具名)
        :param query: 查询参数（企业名称）
        :param api_key: 可选 API Key 覆盖
        :param retry: 重试次数
        """
        service_config = self.mcp_servers.get(server_id)
        if not service_config:
            return {"error": f"MCP server '{server_id}' not configured."}

        url = service_config["url"]
        headers = service_config["headers"].copy()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"

        payload = {"query": query}
        last_error = None

        for attempt in range(retry + 1):
            try:
                print(f"[QccMcpClient] Calling {server_id} for: {query} (attempt {attempt + 1}/{retry + 1})")
                response = self.session.post(url, headers=headers,
                                            json=payload, stream=True, timeout=30)
                response.raise_for_status()
                return self._parse_sse_response(response)
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout: {e}"
                print(f"  [Retry {attempt + 1}/{retry}] Timeout error")
            except requests.exceptions.ConnectionError as e:
                last_error = f"Connection Error: {e}"
                print(f"  [Retry {attempt + 1}/{retry}] Connection error")
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP Error {e.response.status_code}: {e.response.text}"
                print(f"  [Retry {attempt + 1}/{retry}] HTTP error: {e.response.status_code}")
            except Exception as e:
                last_error = f"Error: {e}"
                print(f"  [Retry {attempt + 1}/{retry}] Error: {e}")

        return {"error": f"Max retries exceeded. Last error: {last_error}"}

    def _parse_sse_response(self, response) -> Dict:
        """解析 SSE 流式响应 - V2 增强：完整处理和错误检测"""
        full_data = []
        error_messages = []

        try:
            for line in response.iter_lines():
                if line:
                    decoded = line.decode('utf-8')
                    if decoded.startswith('data:'):
                        try:
                            json_data = json.loads(decoded[5:])
                            # 检测错误事件
                            if json_data.get("event") == "error" or json_data.get("error"):
                                error_msg = json_data.get("message", json_data.get("error", "Unknown error"))
                                error_messages.append(error_msg)
                            elif json_data.get("event") == "data" and "data" in json_data:
                                full_data.append(json_data["data"])
                            elif json_data.get("event") == "end":
                                break
                            else:
                                full_data.append(json_data)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            return {"error": f"Failed to parse SSE response: {e}"}

        if error_messages:
            return {"error": "; ".join(error_messages)}

        if not full_data:
            return {"error": "No data received from MCP service"}

        return {"data": full_data[0] if len(full_data) == 1 else full_data, "count": len(full_data)}

    def check_health(self) -> Dict[str, bool]:
        """V2 新增：检查所有服务健康状态"""
        status = {}
        for server_id in self.mcp_servers:
            try:
                result = self.call_mcp_service(server_id, "test", retry=0)
                status[server_id] = "error" not in result
            except:
                status[server_id] = False
        return status

    def get_configured_servers(self) -> List[str]:
        """V2 新增：获取已配置的服务器列表"""
        return list(self.mcp_servers.keys())
