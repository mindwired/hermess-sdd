from __future__ import annotations

import tempfile
import unittest
from pathlib import Path


try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover - optional outside Hermes
    TestClient = None


@unittest.skipIf(TestClient is None, "FastAPI/HTTPX test support is not installed")
class DashboardApiTest(unittest.TestCase):
    def test_health_source_and_project_lifecycle(self) -> None:
        from fastapi import FastAPI

        from hermes_sdd.core import SDDService
        from hermes_sdd.dashboard_api import create_router
        from hermes_sdd.registry import SourceRegistry

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp)
            root = base / "repo"
            root.mkdir()
            app = FastAPI()
            app.include_router(create_router(SDDService(SourceRegistry(base / "registry.db"))))
            client = TestClient(app)
            self.assertEqual(client.get("/health").status_code, 200)
            registered = client.post("/sources", json={"path": str(root), "name": "Example"})
            self.assertEqual(registered.status_code, 200)
            initialized = client.post(
                "/operation",
                json={
                    "operation": "init",
                    "root": str(root),
                    "payload": {"goal": "Build it", "mode": "quick"},
                },
            )
            self.assertEqual(initialized.status_code, 200)
            snapshot = client.get("/snapshot", params={"root": str(root)})
            self.assertEqual(snapshot.status_code, 200)
            self.assertEqual(snapshot.json()["project"]["goal"], "Build it")

    def test_rejects_invalid_operation_without_leaking_traceback(self) -> None:
        from fastapi import FastAPI

        from hermes_sdd.dashboard_api import create_router

        app = FastAPI()
        app.include_router(create_router())
        client = TestClient(app)
        response = client.post("/operation", json={"operation": "not-a-real-operation"})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"].split(":", 1)[0], "ValueError")


if __name__ == "__main__":
    unittest.main()
