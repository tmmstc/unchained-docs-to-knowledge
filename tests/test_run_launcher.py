"""
Tests for the ApplicationLauncher in run.py.
"""

import sys
import importlib.util


def test_application_launcher_executable_mode_flag():
    """Test that ApplicationLauncher respects executable_mode flag."""
    spec = importlib.util.spec_from_file_location("run", "run.py")
    run_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_module)

    launcher_dev = run_module.ApplicationLauncher(executable_mode=False)
    assert launcher_dev.executable_mode is False

    launcher_exe = run_module.ApplicationLauncher(executable_mode=True)
    assert launcher_exe.executable_mode is True


def test_application_launcher_frozen_detection():
    """Test that ApplicationLauncher detects frozen executable."""
    spec = importlib.util.spec_from_file_location("run", "run.py")
    run_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_module)

    original_frozen = getattr(sys, "frozen", None)
    original_meipass = getattr(sys, "_MEIPASS", None)

    try:
        sys.frozen = True
        sys._MEIPASS = "/tmp/fake"
        launcher_auto = run_module.ApplicationLauncher()
        assert launcher_auto.executable_mode is True
    finally:
        if original_frozen is None:
            if hasattr(sys, "frozen"):
                delattr(sys, "frozen")
        else:
            sys.frozen = original_frozen

        if original_meipass is None:
            if hasattr(sys, "_MEIPASS"):
                delattr(sys, "_MEIPASS")
        else:
            sys._MEIPASS = original_meipass


def test_parse_args():
    """Test argument parsing."""
    spec = importlib.util.spec_from_file_location("run", "run.py")
    run_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(run_module)

    original_argv = sys.argv

    try:
        sys.argv = ["run.py"]
        args = run_module.parse_args()
        assert args.executable_mode is False
        assert args.no_browser is False

        sys.argv = ["run.py", "--executable-mode"]
        args = run_module.parse_args()
        assert args.executable_mode is True

        sys.argv = ["run.py", "--no-browser"]
        args = run_module.parse_args()
        assert args.no_browser is True
    finally:
        sys.argv = original_argv
