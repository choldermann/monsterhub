import docker
from concurrent.futures import ThreadPoolExecutor, as_completed
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

    def update_monster(self, containers: List[str]) -> dict:
        pulled = []
        already_latest = []
        skipped = []
        errors = []

        for name in containers:
            try:
                c = self.client.containers.get(name)
            except docker.errors.NotFound:
                skipped.append(name)
                continue

            image_name = c.attrs.get("Config", {}).get("Image", "")
            old_image_id = c.attrs.get("Image", "")

            if not image_name or image_name.startswith("sha256:"):
                skipped.append(name)
                continue

            try:
                new_image = self.client.images.pull(image_name)
                if new_image.id != old_image_id:
                    pulled.append(name)
                else:
                    already_latest.append(name)
            except Exception:
                skipped.append(name)

        if pulled:
            for name in containers:
                try:
                    self.client.containers.get(name).restart()
                except Exception:
                    errors.append(name)

        return {
            "updated": len(pulled) > 0,
            "pulled": pulled,
            "already_latest": already_latest,
            "skipped": skipped,
            "errors": errors,
        }

    def get_monster_stats(self, containers: List[str]) -> dict:
        running = [n for n in containers if self._is_running(n)]
        if not running:
            return {"cpu_percent": None, "mem_mb": None, "mem_percent": None, "containers": []}

        results = []
        with ThreadPoolExecutor(max_workers=len(running)) as ex:
            futures = {ex.submit(self._container_stats, n): n for n in running}
            for f in as_completed(futures):
                results.append(f.result())

        total_cpu = sum(r["cpu_percent"] for r in results if r["cpu_percent"] is not None)
        total_mem_mb = sum(r["mem_mb"] for r in results if r["mem_mb"] is not None)
        total_mem_percent = sum(r["mem_percent"] for r in results if r["mem_percent"] is not None)

        return {
            "cpu_percent": round(total_cpu, 1),
            "mem_mb": round(total_mem_mb, 1),
            "mem_percent": round(total_mem_percent, 1),
            "containers": sorted(results, key=lambda r: r["name"]),
        }

    def _is_running(self, name: str) -> bool:
        try:
            return self.client.containers.get(name).status == "running"
        except Exception:
            return False

    def _container_stats(self, name: str) -> dict:
        try:
            c = self.client.containers.get(name)
            s = c.stats(stream=False)
            cpu = self._calc_cpu(s)
            mem_percent, mem_mb = self._calc_mem(s)
            return {"name": name, "cpu_percent": round(cpu, 1), "mem_percent": round(mem_percent, 1), "mem_mb": round(mem_mb, 1)}
        except Exception:
            return {"name": name, "cpu_percent": None, "mem_percent": None, "mem_mb": None}

    @staticmethod
    def _calc_cpu(s: dict) -> float:
        try:
            cpu_delta = s["cpu_stats"]["cpu_usage"]["total_usage"] - s["precpu_stats"]["cpu_usage"]["total_usage"]
            sys_delta = s["cpu_stats"]["system_cpu_usage"] - s["precpu_stats"]["system_cpu_usage"]
            cpus = s["cpu_stats"].get("online_cpus") or len(s["cpu_stats"]["cpu_usage"].get("percpu_usage", [1]))
            return (cpu_delta / sys_delta) * cpus * 100 if sys_delta > 0 else 0.0
        except Exception:
            return 0.0

    @staticmethod
    def _calc_mem(s: dict) -> tuple[float, float]:
        try:
            ms = s["memory_stats"]
            usage = ms["usage"]
            limit = ms["limit"]
            inner = ms.get("stats", {})
            cache = inner.get("cache", inner.get("inactive_file", 0))
            actual = max(0, usage - cache)
            return (actual / limit * 100) if limit > 0 else 0.0, actual / (1024 * 1024)
        except Exception:
            return 0.0, 0.0

    def get_logs(self, container_name: str, lines: int = 150) -> str:
        try:
            c = self.client.containers.get(container_name)
            return c.logs(tail=lines, timestamps=True).decode("utf-8", errors="replace")
        except docker.errors.NotFound:
            return f"Container '{container_name}' nicht gefunden."
        except Exception as e:
            return str(e)
