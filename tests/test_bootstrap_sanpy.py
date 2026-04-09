import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import san

from scripts.bootstrap_sanpy import configure_san


class BootstrapSanpyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.original_api_key = san.ApiConfig.api_key

    def tearDown(self) -> None:
        san.ApiConfig.api_key = self.original_api_key

    def test_prefers_environment_variable(self) -> None:
        with patch.dict(os.environ, {"SAN_API_KEY": "env-key"}, clear=True):
            api_key = configure_san()

        self.assertEqual(api_key, "env-key")
        self.assertEqual(san.ApiConfig.api_key, "env-key")

    def test_reads_repo_env_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)
            (repo_root / ".env").write_text("SAN_API_KEY=file-key\n")

            with patch.dict(os.environ, {}, clear=True):
                api_key = configure_san(repo_root=repo_root)

        self.assertEqual(api_key, "file-key")
        self.assertEqual(san.ApiConfig.api_key, "file-key")

    def test_raises_without_api_key(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repo_root = Path(temp_dir)

            with patch.dict(os.environ, {}, clear=True):
                with self.assertRaisesRegex(RuntimeError, "SAN_API_KEY is required"):
                    configure_san(repo_root=repo_root)


if __name__ == "__main__":
    unittest.main()
