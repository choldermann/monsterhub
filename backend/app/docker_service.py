import docker
from typing import List, Optional


class DockerService:
    def __init__(self):
        self.client = docker.from_env()

    def get_container_info(self, name: str) -> dict:
        try:
            c = self.client.containers.get(name)
        except docker.errors.NotFound:
            return {"name": name, "status": "not_found", "version": None}
        except Exception:
            return {"name": name, "status": "error", "version": None}

        try:
            tags = c.image.tags
            version = tags[0].split(":")[-1] if tags else "—"
        except Exception:
            version = "—"

        return {"name": name, "status": c.status, "version": version}

    def get_monster_status(self, containers: List[str]) -> dict:
        if not containers:
            return {"state": "not_installed", "containers": []}

        infos = [self.get_container_info(c) for c in containers]
        running = sum(1 for i in infos if i["status"] == "running")
        total = len(infos)

        if running == total:
            state = "running"
        elif running == 0:
            state = "stopped"
        else:
            state = "partial"

        return {"state": state, "containers": infos}

    def restart_containers(self, containers: List[str]):
        for name in containers:
            try:
                self.client.containers.get(name).restart()
            except docker.errors.NotFound:
                pass

    def stop_containers(self, containers: List[str]):
        for name in containers:
            try:
                self.client.containers.get(name).stop()
            except docker.errors.NotFound:
                pass

    def start_containers(self, containers: List[str]):
        for name in containers:
            try:
                self.client.containers.get(name).start()
            except docker.errors.NotFound:
                pass

    def get_logs(self, container_name: str, lines: int = 150) -> str:
        try:
            c = self.client.containers.get(container_name)
            return c.logs(tail=lines, timestamps=True).decode("utf-8", errors="replace")
        except docker.errors.NotFound:
            return f"Container '{container_name}' nicht gefunden."
        except Exception as e:
            return str(e)
