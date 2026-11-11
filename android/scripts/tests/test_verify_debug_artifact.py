"""Offline tests for Android artifact manifest; no Android SDK or network required."""
from pathlib import Path
import hashlib
import tempfile
import unittest
from zipfile import ZipFile
from scripts.verify_debug_artifact import verify

SHA = "a" * 40
RUN = "https://github.com/onnxscibroccoli/accubook/actions/runs/123456"
GRADLE = """android {
  defaultConfig {
    applicationId 'com.accubook.crm'
    versionName '0.5.0-dev.1'
  }
}
"""

class DebugArtifactTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.apk = self.root / "app-debug.apk"
        with ZipFile(self.apk, "w") as z:
            z.writestr("AndroidManifest.xml", b"manifest")
            z.writestr("classes.dex", b"dex")
        self.checksum = self.root / "SHA256SUMS.txt"
        self.checksum.write_text(hashlib.sha256(self.apk.read_bytes()).hexdigest() +
                                 "  app/build/outputs/apk/debug/app-debug.apk\n")
        self.gradle = self.root / "build.gradle"
        self.gradle.write_text(GRADLE)

    def test_valid_debug_manifest(self):
        report = verify(self.apk, self.checksum, self.gradle, SHA, RUN)
        self.assertEqual(report["package"], "com.accubook.crm")
        self.assertEqual(report["version_name"], "0.5.0-dev.1")
        self.assertEqual(report["status"], "DEBUG_APK_TEST_ARTIFACT_NOT_RELEASE")
        self.assertEqual(report["sha256"], hashlib.sha256(self.apk.read_bytes()).hexdigest())

    def test_mutation_fails_digest(self):
        with self.apk.open("ab") as f:
            f.write(b"unexpected-bytes")
        with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
            verify(self.apk, self.checksum, self.gradle, SHA, RUN)

    def test_unexpected_package_fails(self):
        self.gradle.write_text(GRADLE.replace("com.accubook.crm", "com.other.app"))
        with self.assertRaisesRegex(ValueError, "application ID"):
            verify(self.apk, self.checksum, self.gradle, SHA, RUN)

    def test_untrusted_checkout_sha_fails(self):
        with self.assertRaisesRegex(ValueError, "source SHA"):
            verify(self.apk, self.checksum, self.gradle, "latest", RUN)

    def test_unrelated_checksum_target_fails(self):
        self.checksum.write_text(hashlib.sha256(self.apk.read_bytes()).hexdigest() +
                                 "  other.apk\n")
        with self.assertRaisesRegex(ValueError, "checksum"):
            verify(self.apk, self.checksum, self.gradle, SHA, RUN)

    def test_not_an_apk_fails(self):
        self.apk.write_bytes(b"not a zip")
        with self.assertRaises(Exception):
            verify(self.apk, self.checksum, self.gradle, SHA, RUN)

if __name__ == "__main__":
    unittest.main()
