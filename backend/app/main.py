from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .docker_service import DockerService
from .config import load_registry

app = FastAPI(title="MonsterHub API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

docker_svc = DockerService()


@app.get("/api/monsters")
def list_monsters():
    registry = load_registry()
    result = []
    for m in registry["monsters"]:
        status = docker_svc.get_monster_status(m["containers"])
        result.append({**m, "status": status})
    return result


def _get_monster(monster_id: str) -> dict:
    registry = load_registry()
    monster = next((m for m in registry["monsters"] if m["id"] == monster_id), None)
    if not monster:
        raise HTTPException(status_code=404, detail="Monster nicht gefunden")
    return monster


@app.post("/api/monsters/{monster_id}/start")
def start_monster(monster_id: str):
    m = _get_monster(monster_id)
    docker_svc.start_containers(m["containers"])
    return {"ok": True}


@app.post("/api/monsters/{monster_id}/stop")
def stop_monster(monster_id: str):
    m = _get_monster(monster_id)
    docker_svc.stop_containers(m["containers"])
    return {"ok": True}


@app.post("/api/monsters/{monster_id}/restart")
def restart_monster(monster_id: str):
    m = _get_monster(monster_id)
    docker_svc.restart_containers(m["containers"])
    return {"ok": True}


@app.post("/api/monsters/{monster_id}/update")
def update_monster(monster_id: str):
    m = _get_monster(monster_id)
    result = docker_svc.update_monster(m["containers"])
    return result


@app.get("/api/monsters/{monster_id}/logs")
def get_logs(monster_id: str, container: Optional[str] = None, lines: int = 150):
    m = _get_monster(monster_id)
    name = container or m.get("primary_container")
    if not name:
        return {"logs": "Keine Container konfiguriert."}
    return {"logs": docker_svc.get_logs(name, lines), "container": name}
