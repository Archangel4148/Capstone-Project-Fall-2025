from unittest.mock import patch

from system.active_window import get_active_window


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

# NOTE: I couldn't find a way to test the lower-level functions for linux, so I am skipping them (they're OS-specific anyway)