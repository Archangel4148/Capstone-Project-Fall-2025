from unittest.mock import MagicMock, patch
import pytest
from notifications import NotificationManager

def test_notify_calls_notifypy(mock_notifications):
    NotificationManager.notify("Test Title", "Test Message")

    # The attributes are set on the mock object by NotificationManager
    assert mock_notifications.application_name == NotificationManager._app_name
    assert mock_notifications.title == "Test Title"
    assert mock_notifications.message == "Test Message"
    mock_notifications.send.assert_called_once()