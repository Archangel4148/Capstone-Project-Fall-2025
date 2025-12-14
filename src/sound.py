from PyQt5.QtCore import QUrl
from PyQt5.QtMultimedia import QSoundEffect

_active_sounds = []

def _cleanup_finished_sounds():
    global _active_sounds
    _active_sounds = [s for s in _active_sounds if s.isPlaying()]


def play_sound(sound_path: str):
    """Play a .wav file located at sound_path."""
    sound = QSoundEffect()
    sound.setSource(QUrl.fromLocalFile(sound_path))
    sound.setLoopCount(1)
    sound.setVolume(1.0)

    # Add to active list to prevent garbage collection
    _active_sounds.append(sound)

    sound.play()
    _cleanup_finished_sounds()

def play_looping_sound(sound_path: str):
    """
    Play a looping .wav file.
    Returns a stop() callback that stops the loop
    """
    sound = QSoundEffect()
    sound.setSource(QUrl.fromLocalFile(sound_path))
    sound.setLoopCount(QSoundEffect.Infinite)
    sound.setVolume(1.0)

    _active_sounds.append(sound)
    sound.play()

    def stop():
        if sound in _active_sounds:
            sound.stop()
            _active_sounds.remove(sound)

    return stop