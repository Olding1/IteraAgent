"""UV Downloader - Automatic uv binary downloader.

This module handles automatic downloading and setup of the uv package manager.
"""

import os
import sys
import urllib.request
from pathlib import Path
from typing import Optional


class UVDownloader:
    """Automatic uv binary downloader to project directory."""

    UV_VERSION = "0.5.11"  # Latest stable version as of 2026-01
    UV_URLS = {
        "win32": f"https://github.com/astral-sh/uv/releases/download/{UV_VERSION}/uv-x86_64-pc-windows-msvc.zip",
        "linux": f"https://github.com/astral-sh/uv/releases/download/{UV_VERSION}/uv-x86_64-unknown-linux-gnu.tar.gz",
        "darwin": f"https://github.com/astral-sh/uv/releases/download/{UV_VERSION}/uv-x86_64-apple-darwin.tar.gz",
    }

    def __init__(self, project_root: Path):
        """Initialize UV downloader.

        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root)
        self.bin_dir = self.project_root / "bin"
        self.uv_path = self.bin_dir / ("uv.exe" if sys.platform == "win32" else "uv")

    def ensure_uv(self) -> Path:
        """Ensure uv is available, download if not exists.

        Returns:
            Path to uv executable

        Raises:
            RuntimeError: If download fails
        """
        if self.uv_path.exists():
            print(f"✅ uv already exists: {self.uv_path}")
            return self.uv_path

        # Create bin directory
        self.bin_dir.mkdir(parents=True, exist_ok=True)

        # Download uv
        url = self.UV_URLS.get(sys.platform)
        if not url:
            raise RuntimeError(f"Unsupported platform: {sys.platform}")

        print(f"⬇️  Downloading uv ({sys.platform})...")
        print(f"   URL: {url}")

        try:
            with urllib.request.urlopen(url, timeout=60) as response:
                content = response.read()

                # For Windows, download is a zip file
                if sys.platform == "win32":
                    import zipfile
                    import io

                    zip_file = zipfile.ZipFile(io.BytesIO(content))
                    # Extract uv.exe
                    for name in zip_file.namelist():
                        if name.endswith("uv.exe"):
                            with zip_file.open(name) as source:
                                self.uv_path.write_bytes(source.read())
                            break
                else:
                    # For Unix, download is a tar.gz file
                    import tarfile
                    import io

                    tar_file = tarfile.open(fileobj=io.BytesIO(content), mode="r:gz")
                    # Extract uv binary
                    for member in tar_file.getmembers():
                        if member.name.endswith("/uv") or member.name == "uv":
                            with tar_file.extractfile(member) as source:
                                self.uv_path.write_bytes(source.read())
                            break

                    # Set executable permission (Unix)
                    os.chmod(self.uv_path, 0o755)

        except Exception as e:
            raise RuntimeError(f"Failed to download uv: {e}")

        if not self.uv_path.exists():
            raise RuntimeError("uv binary not found in downloaded archive")

        print(f"✅ uv ready: {self.uv_path}")
        return self.uv_path

    def get_version(self) -> Optional[str]:
        """Get uv version.

        Returns:
            Version string or None if uv not available
        """
        if not self.uv_path.exists():
            return None

        import subprocess

        try:
            result = subprocess.run(
                [str(self.uv_path), "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception:
            pass

        return None
