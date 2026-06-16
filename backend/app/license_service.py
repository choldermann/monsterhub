import httpx
from .settings_service import load_settings


async def check_license(monster_id: str) -> dict:
    settings = load_settings()
    url = settings.get("monstersuite_url", "https://monstersuite.de").rstrip("/")
    key = settings.get("license_keys", {}).get(monster_id, "").strip()

    if not key:
        return {"configured": False}

    try:
        async with httpx.AsyncClient(timeout=8) as client:
            r = await client.get(f"{url}/api/v1/licenses/status", params={"key": key})
            data = r.json()
            data["configured"] = True
            return data
    except httpx.TimeoutException:
        return {"configured": True, "valid": False, "error": "timeout"}
    except Exception:
        return {"configured": True, "valid": False, "error": "unreachable"}
