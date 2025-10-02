#!/usr/bin/env python3
"""
Cross-platform development server startup script.
Works on Windows, Linux, and macOS.
"""
import subprocess
import sys
from pathlib import Path


def main():
    """Start the development environment in a cross-platform way."""
    # Change to project root
    project_root = Path(__file__).parent.parent.resolve()

    print(f"Starting development environment from: {project_root}")

    # Check for virtual environment
    venv_dir = project_root / "venv"
    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"

    # Create venv if it doesn't exist
    if not venv_dir.exists():
        print("Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", str(venv_dir)], check=True, cwd=project_root)
        print("✅ Virtual environment created")

    # Upgrade pip
    print("Upgrading pip...")
    subprocess.run(
        [str(venv_python), "-m", "pip", "install", "--upgrade", "pip"], check=True, cwd=project_root
    )

    # Install dependencies
    print("Installing dependencies...")
    requirements_file = project_root / "requirements.txt"
    subprocess.run(
        [str(venv_pip), "install", "-r", str(requirements_file)], check=True, cwd=project_root
    )
    print("✅ Dependencies installed")

    # Run the launcher
    print("\nStarting application...")
    run_script = project_root / "run.py"
    subprocess.run([str(venv_python), str(run_script)], cwd=project_root)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n🛑 Development server stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
