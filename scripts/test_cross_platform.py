#!/usr/bin/env python3
"""
Test cross-platform compatibility of script utilities.
Verifies path handling, platform detection, and virtual environment logic.
"""
import sys
from pathlib import Path


def test_platform_detection():
    """Test platform detection."""
    print("=" * 80)
    print("PLATFORM DETECTION TEST")
    print("=" * 80)
    print(f"Platform: {sys.platform}")
    print(f"Python version: {sys.version}")

    if sys.platform == "win32":
        print("✅ Detected Windows platform")
        expected_venv_subdir = "Scripts"
    elif sys.platform in ("linux", "darwin"):
        print(f"✅ Detected POSIX platform ({sys.platform})")
        expected_venv_subdir = "bin"
    else:
        print(f"⚠️ Unknown platform: {sys.platform}")
        expected_venv_subdir = "bin"

    print(f"Expected venv subdirectory: {expected_venv_subdir}")
    return expected_venv_subdir


def test_path_handling():
    """Test pathlib usage for cross-platform paths."""
    print("\n" + "=" * 80)
    print("PATH HANDLING TEST")
    print("=" * 80)

    # Get script and project paths
    script_path = Path(__file__)
    project_root = script_path.parent.parent.resolve()

    print(f"Script path: {script_path}")
    print(f"Project root: {project_root}")

    # Test path construction
    venv_dir = project_root / "venv"
    frontend_dir = project_root / "frontend"
    app_dir = project_root / "app"

    print(f"\nVirtual env dir: {venv_dir}")
    print(f"Frontend dir: {frontend_dir}")
    print(f"App dir: {app_dir}")

    # Check existence
    print("\nDirectory existence:")
    print(f"  venv: {venv_dir.exists()}")
    print(f"  frontend: {frontend_dir.exists()}")
    print(f"  app: {app_dir.exists()}")

    return project_root


def test_venv_detection(project_root, expected_venv_subdir):
    """Test virtual environment detection."""
    print("\n" + "=" * 80)
    print("VIRTUAL ENVIRONMENT DETECTION TEST")
    print("=" * 80)

    venv_dir = project_root / "venv"

    if sys.platform == "win32":
        venv_python = venv_dir / "Scripts" / "python.exe"
        venv_pip = venv_dir / "Scripts" / "pip.exe"
    else:
        venv_python = venv_dir / "bin" / "python"
        venv_pip = venv_dir / "bin" / "pip"

    print(f"Expected Python: {venv_python}")
    print(f"Expected pip: {venv_pip}")

    if venv_python.exists():
        print(f"✅ Found virtual environment Python at: {venv_python}")
    else:
        print(f"⚠️ Virtual environment Python not found at: {venv_python}")
        print("   This is OK if venv is not yet created")

    if venv_pip.exists():
        print(f"✅ Found virtual environment pip at: {venv_pip}")
    else:
        print(f"⚠️ Virtual environment pip not found at: {venv_pip}")
        print("   This is OK if venv is not yet created")

    return venv_python.exists()


def test_import_path_construction():
    """Test import path construction."""
    print("\n" + "=" * 80)
    print("IMPORT PATH CONSTRUCTION TEST")
    print("=" * 80)

    script_path = Path(__file__)
    parent_dir = script_path.parent.parent.resolve()

    print(f"Adding to sys.path: {parent_dir}")

    # Verify it's a valid path
    if parent_dir.exists():
        print("✅ Import path exists")

        # Check for expected directories
        app_dir = parent_dir / "app"
        frontend_dir = parent_dir / "frontend"

        if app_dir.exists():
            print("✅ app/ directory found")
        if frontend_dir.exists():
            print("✅ frontend/ directory found")
    else:
        print("❌ Import path does not exist!")


def main():
    """Run all tests."""
    print("\n" + "=" * 80)
    print("CROSS-PLATFORM SCRIPT COMPATIBILITY TEST")
    print("=" * 80 + "\n")

    expected_venv_subdir = test_platform_detection()
    project_root = test_path_handling()
    venv_exists = test_venv_detection(project_root, expected_venv_subdir)
    test_import_path_construction()

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Platform: {sys.platform}")
    print(f"Python: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"Virtual env exists: {venv_exists}")
    print(f"Project root: {project_root}")
    print("\n✅ All cross-platform compatibility tests completed!")
    print("\nNOTE: Scripts use pathlib.Path for all path operations")
    print("      and sys.platform for platform-specific logic.")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
