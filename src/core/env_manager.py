"""Environment manager for creating and managing virtual environments."""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional
from pydantic import BaseModel, Field

from ..utils.uv_downloader import UVDownloader
from ..utils.performance_metrics import PerformanceMetrics


class EnvSetupResult(BaseModel):
    """Result of environment setup."""

    success: bool = Field(..., description="Whether setup succeeded")
    venv_path: Path = Field(..., description="Path to virtual environment")
    python_executable: Path = Field(..., description="Path to Python executable")
    error_message: Optional[str] = Field(
        default=None, description="Error message if setup failed"
    )
    used_uv: bool = Field(default=False, description="Whether uv was used")
    metrics: Optional[dict] = Field(default=None, description="Performance metrics")


class EnvManager:
    """Manager for creating and managing isolated Python virtual environments.
    
    Handles venv creation, dependency installation, and environment activation
    without requiring Docker.
    """

    def __init__(self, agent_dir: Path, use_uv: bool = True):
        """Initialize environment manager.
        
        Args:
            agent_dir: Path to agent project directory
            use_uv: Whether to use uv for faster installation (default: True)
        """
        self.agent_dir = Path(agent_dir).resolve()  # Convert to absolute path
        self.venv_path = self.agent_dir / ".venv"
        self._python_exe: Optional[Path] = None
        self.use_uv = use_uv
        self._uv_path: Optional[Path] = None
        self.metrics = PerformanceMetrics()
        
        # Initialize UV downloader if enabled
        if self.use_uv:
            project_root = self.agent_dir.parent.parent  # Assume agents/xxx structure
            self.uv_downloader = UVDownloader(project_root)

    def setup_environment(self) -> EnvSetupResult:
        """Create virtual environment and install dependencies.
        
        Returns:
            EnvSetupResult with success status and paths
        """
        used_uv = False
        
        try:
            # Try uv first if enabled
            if self.use_uv:
                try:
                    return self._setup_with_uv()
                except Exception as e:
                    print(f"⚠️  uv setup failed: {e}")
                    print("   Falling back to venv...")
            
            # Fallback to standard venv
            return self._setup_with_venv()

        except Exception as e:
            return EnvSetupResult(
                success=False,
                venv_path=self.venv_path,
                python_executable=Path(""),
                error_message=f"Environment setup failed: {str(e)}",
                used_uv=used_uv,
                metrics=self.metrics.to_dict()
            )
    
    def _setup_with_uv(self) -> EnvSetupResult:
        """Setup environment using uv.
        
        Returns:
            EnvSetupResult
        """
        print("⚡ Using uv for fast environment setup...")
        
        # Ensure uv is available
        self.metrics.start_timer("download")
        self._uv_path = self.uv_downloader.ensure_uv()
        self.metrics.stop_timer("download")
        
        # Create venv if it doesn't exist
        if not self.venv_path.exists():
            print(f"⚡ Creating virtual environment with uv...")
            self.metrics.start_timer("venv_create")
            self._create_venv_with_uv()
            self.metrics.stop_timer("venv_create")

        # Get Python executable
        python_exe = self.get_python_executable()

        # Install requirements
        requirements_file = self.agent_dir / "requirements.txt"
        if requirements_file.exists():
            print("⚡ Installing dependencies with uv...")
            self.metrics.start_timer("install")
            install_success = self._install_with_uv(requirements_file)
            self.metrics.stop_timer("install")
            
            if not install_success:
                raise RuntimeError("uv pip install failed")
        
        # Report performance
        self.metrics.report()

        return EnvSetupResult(
            success=True,
            venv_path=self.venv_path,
            python_executable=python_exe,
            used_uv=True,
            metrics=self.metrics.to_dict()
        )
    
    def _setup_with_venv(self) -> EnvSetupResult:
        """Setup environment using standard venv.
        
        Returns:
            EnvSetupResult
        """
        print("Using standard venv...")
        
        # Create venv if it doesn't exist
        if not self.venv_path.exists():
            print(f"Creating virtual environment at {self.venv_path}...")
            self.metrics.start_timer("venv_create")
            self._create_venv()
            self.metrics.stop_timer("venv_create")

        # Get Python executable
        python_exe = self.get_python_executable()

        # Install requirements
        requirements_file = self.agent_dir / "requirements.txt"
        if requirements_file.exists():
            print("Installing dependencies...")
            self.metrics.start_timer("install")
            install_success = self.install_requirements()
            self.metrics.stop_timer("install")
            
            if not install_success:
                return EnvSetupResult(
                    success=False,
                    venv_path=self.venv_path,
                    python_executable=python_exe,
                    error_message="Failed to install dependencies",
                    used_uv=False,
                    metrics=self.metrics.to_dict()
                )
        
        # Report performance
        self.metrics.report()

        return EnvSetupResult(
            success=True,
            venv_path=self.venv_path,
            python_executable=python_exe,
            used_uv=False,
            metrics=self.metrics.to_dict()
        )

    def _create_venv(self) -> None:
        """Create virtual environment using venv module."""
        process = self._run_command(
            [sys.executable, "-m", "venv", str(self.venv_path)], cwd=self.agent_dir
        )

        if process.returncode != 0:
            raise RuntimeError(f"Failed to create venv: {process.stderr}")
    
    def _create_venv_with_uv(self) -> None:
        """Create virtual environment using uv."""
        cmd = [str(self._uv_path), "venv", str(self.venv_path)]
        process = self._run_command(cmd, cwd=self.agent_dir, timeout=10)
        
        if process.returncode != 0:
            raise RuntimeError(f"uv venv failed: {process.stderr}")

    def get_python_executable(self) -> Path:
        """Get path to Python executable in virtual environment.
        
        Returns:
            Path to Python executable
        """
        if self._python_exe is not None:
            return self._python_exe

        # Determine platform-specific path
        if sys.platform == "win32":
            python_exe = self.venv_path / "Scripts" / "python.exe"
        else:
            python_exe = self.venv_path / "bin" / "python"

        if not python_exe.exists():
            raise FileNotFoundError(f"Python executable not found at {python_exe}")

        self._python_exe = python_exe
        return python_exe

    def install_requirements(self) -> bool:
        """Install dependencies from requirements.txt.
        
        Returns:
            True if installation succeeded, False otherwise
        """
        python_exe = self.get_python_executable()
        requirements_file = self.agent_dir / "requirements.txt"

        if not requirements_file.exists():
            print("No requirements.txt found, skipping installation")
            return True

        # Configure pip to use mirror (for faster installation in China)
        pip_config = self._get_pip_config()

        # Install dependencies
        cmd = [
            str(python_exe),
            "-m",
            "pip",
            "install",
            "-r",
            str(requirements_file),
        ]

        # Add mirror configuration
        if pip_config:
            cmd.extend(["-i", pip_config["index_url"]])

        print(f"Running: {' '.join(cmd)}")
        process = self._run_command(cmd, cwd=self.agent_dir, timeout=300)

        if process.returncode != 0:
            print(f"Installation failed: {process.stderr}")
            return False

        print("Dependencies installed successfully")
        return True
    
    def _install_with_uv(self, requirements_file: Path) -> bool:
        """Install dependencies using uv.
        
        Args:
            requirements_file: Path to requirements.txt
            
        Returns:
            True if installation succeeded
        """
        python_exe = self.get_python_executable()
        cmd = [
            str(self._uv_path),
            "pip",
            "install",
            "-q",  # 🆕 Quiet mode
            "-r",
            str(requirements_file),
            "--python",
            str(python_exe)
        ]
        
        # print(f"Running: {' '.join(cmd)}") # 🤫 Suppress command printing
        
        # 🆕 Suppress stdout/stderr unless error
        process = self._run_command(cmd, cwd=self.agent_dir, timeout=300)
        
        if process.returncode != 0:
            print(f"uv pip install failed: {process.stderr}")
            return False
        
        # print("Dependencies installed successfully with uv") # 🤫 Suppress success message
        return True

    def _get_pip_config(self) -> Optional[dict]:
        """Get pip mirror configuration.
        
        Returns:
            Dictionary with pip configuration or None
        """
        # Use Tsinghua mirror for faster installation
        return {
            "index_url": "https://pypi.tuna.tsinghua.edu.cn/simple",
            "trusted_host": "pypi.tuna.tsinghua.edu.cn",
        }

    def _run_command(
        self,
        cmd: list[str],
        cwd: Path,
        timeout: int = 60,
    ) -> subprocess.CompletedProcess:
        """Run command in subprocess.
        
        Args:
            cmd: Command and arguments
            cwd: Working directory
            timeout: Timeout in seconds
            
        Returns:
            CompletedProcess result
        """
        process = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return process

    def cleanup(self) -> None:
        """Remove virtual environment."""
        if self.venv_path.exists():
            import shutil

            shutil.rmtree(self.venv_path)
            print(f"Removed virtual environment at {self.venv_path}")
