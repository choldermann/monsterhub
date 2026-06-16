import os
import httpx
from typing import Optional

MONSTERSUITE_URL = os.getenv("MONSTERSUITE_URL", "https://monstersuite.de").rstrip("/")


def _get_key(monster_id: str) -> Optional[str]:
    key = os.getenv(f"{monster_id.upper()}_LICENSE_KEY", "").strip()
    return key or None


async def check_license(monster_id: str) -> dict:
    key = _get_key(monster_id)
    if not key:
        return {"configured": False}

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(
                f"{MONSTERSUITE_URL}/api/v1/licenses/status",
                params={"key": key},
            )
            data = r.json()
            data["configured"] = True
            return data
    except httpx.TimeoutException:
        return {"configured": True, "valid": False, "error": "timeout"}
    except Exception:
        return {"configured": True, "valid": False, "error": "unreachable"}
