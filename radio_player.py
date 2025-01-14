import vlc

class RadioPlayer:
    """
    A class that wraps VLC functionality.
    Handles play, stop, volume—no UI code here.
    """
    def __init__(self):
        self._player = vlc.MediaPlayer()
        self._current_url = ""

    def play_station(self, stream_url: str):
        """Play the given stream URL."""
        if self._current_url == stream_url:
            # If we're already on this station, no need to re-init
            self._player.play()
            return
        self._current_url = stream_url

        # Create and set VLC media
        media = vlc.Media(stream_url)
        self._player.set_media(media)
        self._player.play()

    def stop_station(self):
        self._player.stop()

    def set_volume(self, volume: int):
        self._player.audio_set_volume(volume)
