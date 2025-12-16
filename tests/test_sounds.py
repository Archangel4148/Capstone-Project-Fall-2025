import pytest
from unittest.mock import MagicMock, patch
import sound
from PyQt5.QtMultimedia import QSoundEffect


@pytest.fixture(autouse=True)
def reset_active_sounds():
    # Clear the global list before each test
    sound._active_sounds.clear()


def test_play_sound_sets_properties_and_calls_cleanup():
    # Make sure play_sound sets things up correctly
    mock_sound = MagicMock()
    with patch("sound.QSoundEffect", return_value=mock_sound):
        sound.play_sound("fake_path.wav")

    # Verify properties are set
    mock_sound.setSource.assert_called_once()
    mock_sound.setLoopCount.assert_called_once_with(1)
    mock_sound.setVolume.assert_called_once_with(1.0)
    mock_sound.play.assert_called_once()

    # Verify the sound is appended
    assert sound._active_sounds[-1] == mock_sound

def test_cleanup_finished_sounds_removes_stopped_sounds():
    playing_sound = MagicMock()
    stopped_sound = MagicMock()
    playing_sound.isPlaying.return_value = True
    stopped_sound.isPlaying.return_value = False

    sound._active_sounds.extend([playing_sound, stopped_sound])
    sound._cleanup_finished_sounds()

    assert playing_sound in sound._active_sounds
    assert stopped_sound not in sound._active_sounds
    
def test_play_looping_sound_returns_stop_callback():
    # Make sure the looping sound gives a valid callback
    mock_sound = MagicMock()

    with patch("sound.QSoundEffect", return_value=mock_sound), \
         patch("sound.QSoundEffect.Infinite", QSoundEffect.Infinite):
        stop_cb = sound.play_looping_sound("loop.wav")

    mock_sound.setSource.assert_called_once()
    mock_sound.setLoopCount.assert_called_once_with(QSoundEffect.Infinite)
    mock_sound.setVolume.assert_called_once_with(1.0)
    mock_sound.play.assert_called_once()

    # Check it's in the active list
    assert mock_sound in sound._active_sounds

    # Stop callback should remove it and call stop
    stop_cb()
    mock_sound.stop.assert_called_once()
    assert mock_sound not in sound._active_sounds

