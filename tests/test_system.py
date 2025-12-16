import sys
from unittest.mock import patch

import pytest

from system.active_window import get_active_window
from system.exe_names import get_exe_names


def test_get_active_window_linux(mocker):
    # Test that get_active_window returns the correct window name on Linux
    mock_active = mocker.patch("system.linux.active_window.get_active_window", return_value="LinuxWindow")

    with patch("sys.platform", "linux"):
        result = get_active_window()

    assert result == "LinuxWindow"
    mock_active.assert_called_once()


def test_get_active_window_win32(mocker):
    # Test that get_active_window returns the correct window name on Windows
    mock_active = mocker.patch("system.win.active_window.get_active_window", return_value="WinWindow")

    with patch("sys.platform", "win32"):
        result = get_active_window()

    assert result == "WinWindow"
    mock_active.assert_called_once()

def test_get_exe_names_linux():
    fake_paths = ["/usr/bin/foo", "/usr/bin/bar"]
    fake_return = {"foo": "FooApp", "bar": "BarApp"}

    from system.exe_names import get_exe_names

    # Patch sys.platform to linux
    with patch.object(sys, "platform", "linux"):
        # Patch the module that would be imported
        with patch("system.linux.exe_names.get_exe_names", return_value=fake_return) as mock_func:
            result = get_exe_names(fake_paths)
            mock_func.assert_called_once_with(fake_paths)
            assert result == fake_return

def test_get_exe_names_win32():
    fake_paths = ["C:\\Program Files\\Foo.exe"]
    fake_return = {"Foo.exe": "FooApp"}

    from system.exe_names import get_exe_names

    with patch.object(sys, "platform", "win32"):
        with patch("system.win.exe_names.get_exe_names", return_value=fake_return) as mock_func:
            result = get_exe_names(fake_paths)
            mock_func.assert_called_once_with(fake_paths)
            assert result == fake_return

def test_get_exe_names_unsupported():
    fake_paths = ["/some/path"]
    with patch.object(sys, "platform", "unsupported_os"):
        with pytest.raises(ValueError, match="Unsupported operating system: unsupported_os"):
            get_exe_names(fake_paths)

# NOTE: I couldn't find a way to test the lower-level functions for linux, so I am skipping them (they're OS-specific anyway)