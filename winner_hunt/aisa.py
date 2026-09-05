"""Мінімальний клієнт AIsa (MCP через HTTP).

AIsa — це MCP-шлюз, а не звичайний REST API, тому тут реалізовано рівно
стільки протоколу, скільки треба агенту: initialize -> tools/call.

Ключ читається зі змінної оточення AISA_API_KEY і ніде не логується.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request

ENDPOINT = os.environ.get("AISA_ENDPOINT", "https://mcp.aisa.one/mcp")
PROTOCOL_VERSION = "2025-06-18"

# Шлюз бере приблизно подвійну ціну від DataForSEO, а max_price_usd рахується
# по найгіршому сценарію, а не по факту. Тому ліміти тут із запасом:
# реальний Amazon-виклик коштує ~$0.003, але з лімітом $0.02 не проходить.
DEFAULT_MAX_PRICE_USD = 0.05


class AisaError(RuntimeError):
    pass


class BudgetExceeded(AisaError):
    """Денний ліміт витрат вичерпано — агент зупиняється, а не витрачає далі."""


class Aisa:
    def __init__(self, api_key: str | None = None, budget_usd: float = 0.50):
        self.api_key = api_key or os.environ.get("AISA_API_KEY", "")
        if not self.api_key:
            raise AisaError("AISA_API_KEY не заданий")
        self.budget_usd = budget_usd
        self.spent_usd = 0.0
        self._session_id: str | None = None
        self._initialized = False

    # --- транспорт -------------------------------------------------------

    def _post(self, payload: dict) -> dict | None:
        body = json.dumps(payload).encode()
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {self.api_key}",
            "MCP-Protocol-Version": PROTOCOL_VERSION,
        }
        if self._session_id:
            headers["Mcp-Session-Id"] = self._session_id

        req = urllib.request.Request(ENDPOINT, data=body, headers=headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                sid = resp.headers.get("Mcp-Session-Id")
                if sid:
                    self._session_id = sid
                raw = resp.read().decode()
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode()[:300]
            raise AisaError(f"AIsa HTTP {exc.code}: {detail}") from exc

        if not raw.strip():
            return None
        # Відповідь буває або чистим JSON, або SSE (data: {...}).
        if raw.lstrip().startswith("{"):
            return json.loads(raw)
        for line in raw.splitlines():
            if line.startswith("data:"):
                return json.loads(line[5:].strip())
        raise AisaError(f"Незрозуміла відповідь AIsa: {raw[:200]}")

    def _ensure_session(self) -> None:
        if self._initialized:
            return
        self._post(
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": PROTOCOL_VERSION,
                    "capabilities": {},
                    "clientInfo": {"name": "winner-hunt", "version": "1.0"},
                },
            }
        )
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})
        self._initialized = True

    # --- виклики ---------------------------------------------------------

    def call(self, tool: str, arguments: dict) -> dict:
        self._ensure_session()
        if self.spent_usd >= self.budget_usd:
            raise BudgetExceeded(
                f"витрачено ${self.spent_usd:.4f} з ліміту ${self.budget_usd:.2f}"
            )

        resp = self._post(
            {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/call",
                "params": {"name": tool, "arguments": arguments},
            }
        )
        if resp is None:
            raise AisaError(f"{tool}: порожня відповідь")
        if "error" in resp:
            raise AisaError(f"{tool}: {resp['error']}")

        content = resp.get("result", {}).get("content", [])
        text = next((c.get("text", "") for c in content if c.get("type") == "text"), "")
        data = json.loads(text) if text else {}
        self.spent_usd += _extract_cost(data) * 2  # шлюз бере ~x2 від DataForSEO
        return data

    def use(self, operation_id: str, arguments: dict,
            max_price_usd: float = DEFAULT_MAX_PRICE_USD) -> dict:
        return self.call(
            "use",
            {
                "operation_id": operation_id,
                "arguments": arguments,
                "max_price_usd": max_price_usd,
            },
        )

    def account(self) -> dict:
        """Безкоштовно: баланс, гаманці, витрати за сьогодні."""
        return self.use("account", {}, max_price_usd=0.0)


def _extract_cost(data: dict) -> float:
    """Дістає вартість із конверта DataForSEO; 0.0 якщо її немає."""
    payload = data.get("data", data)
    if isinstance(payload, dict) and isinstance(payload.get("cost"), (int, float)):
        return float(payload["cost"])
    return 0.0
