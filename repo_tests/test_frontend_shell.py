from __future__ import annotations

from pathlib import Path
import unittest


class FrontendShellTests(unittest.TestCase):
    def test_frontend_shell_files_exist(self) -> None:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

        self.assertTrue((frontend_dir / "index.html").exists())
        self.assertTrue((frontend_dir / "app.css").exists())
        self.assertTrue((frontend_dir / "app.js").exists())

    def test_frontend_shell_uses_bff_boundary(self) -> None:
        frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
        index_html = (frontend_dir / "index.html").read_text(encoding="utf-8")
        app_js = (frontend_dir / "app.js").read_text(encoding="utf-8")

        self.assertIn("Frontend externo", index_html)
        self.assertIn("BFF", index_html)
        self.assertIn("window.__CGA_API_BASE__", app_js)
        self.assertIn("/routing", app_js)
        self.assertIn("dashboard.market-overview", app_js)


if __name__ == "__main__":
    unittest.main()
