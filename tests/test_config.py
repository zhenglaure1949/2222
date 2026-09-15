import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agent.config import Config


SECRET_NAMES = (
    "OPENAI_API_KEY",
    "NCBI_API_KEY",
    "BAIDU_APPID",
    "BAIDU_SECRET_KEY",
    "GOOGLE_TRANSLATE_API_KEY",
)


class ConfigSecurityTests(unittest.TestCase):
    def clean_environment(self):
        return patch.dict(os.environ, {name: "" for name in SECRET_NAMES}, clear=False)

    def test_diagnostics_never_return_secret_values(self):
        with self.clean_environment(), patch.dict(os.environ, {"OPENAI_API_KEY": "sk-private-value"}):
            config = Config(env_file="does-not-exist")
            diagnostics = config.get_all()
        self.assertTrue(diagnostics["OPENAI_API_KEY_CONFIGURED"])
        self.assertNotIn("sk-private-value", repr(diagnostics))

    def test_process_environment_wins_over_dotenv(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            env_file = Path(temp_dir) / ".env"
            env_file.write_text("OPENAI_API_KEY=file-secret\n", encoding="utf-8")
            with self.clean_environment(), patch.dict(os.environ, {"OPENAI_API_KEY": "process-secret"}):
                config = Config(env_file=str(env_file))
        self.assertEqual(config.require_secret("OPENAI_API_KEY"), "process-secret")

    def test_missing_secret_fails_closed_without_value(self):
        with self.clean_environment():
            config = Config(env_file="does-not-exist")
        with self.assertRaisesRegex(RuntimeError, "OPENAI_API_KEY"):
            config.require_secret("OPENAI_API_KEY")

    def test_placeholder_secret_is_rejected(self):
        with self.clean_environment(), patch.dict(os.environ, {"NCBI_API_KEY": "your_ncbi_api_key_here"}):
            with self.assertRaisesRegex(ValueError, "NCBI_API_KEY"):
                Config(env_file="does-not-exist")

    def test_api_base_rejects_embedded_credentials(self):
        unsafe = "https://user:private-password@example.com/v1?token=private-token"
        with self.clean_environment(), patch.dict(os.environ, {"OPENAI_API_BASE": unsafe}):
            with self.assertRaisesRegex(ValueError, "must not contain credentials"):
                Config(env_file="does-not-exist")


if __name__ == "__main__":
    unittest.main()
