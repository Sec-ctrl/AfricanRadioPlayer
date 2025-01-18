import vlc
import re


class RadioPlayer:
    """
    A class that wraps VLC functionality.
    Handles play, stop, volume—no UI code here.
    """

    def __init__(self, stations=None):
        self._player = vlc.MediaPlayer()
        self._current_url = ""
        self._event_manager = self._player.event_manager()
        self._stations = stations or []  # Initialize with empty list if no stations are provided

        # Register event callbacks
        self._event_manager.event_attach(
            vlc.EventType.MediaPlayerEncounteredError, self._handle_error_event
        )
        self._event_manager.event_attach(
            vlc.EventType.MediaPlayerStopped, self._handle_stopped_event
        )

    def _handle_error_event(self, event):
        """
        Callback for when VLC encounters a playback error.
        This can happen if the stream URL is invalid or if there's a network issue.
        """
        # You might want to handle reconnection logic, logs, or user notifications here.
        print("VLC encountered an error during playback.")

    def _handle_stopped_event(self, event):
        """
        Callback for when VLC stops playing.
        """
        # This event is fired when `stop_station` is called,
        # or if the media ended on its own and changed state to 'Stopped.'
        print("VLC has stopped playback.")
    
    @staticmethod
    def is_valid_url(url):
        """Validate if the URL is a well-formed HTTP(S) URL."""
        from urllib.parse import urlparse
        try:
            result = urlparse(url)
            return result.scheme in {"http", "https"} and result.netloc != ""
        except Exception:
            return False

    def get_state(self):
        return self._player.get_state()

    def play_station(self, stream_url: str):
        """
        Play the given stream URL.
        
        Edge case handling:
        - If the provided URL is empty, do nothing (or raise an exception).
        - If we're already playing this station, just resume.
        - Attempt to create a new media object and handle any exceptions.
        """
        URL_REGEX_HTTPS = re.compile(r"^https://([^/]+)(.*)$")
        URL_REGEX_HTTP = re.compile(r"^http://([^/]+)(.*)$")

        if not stream_url:
            print("Error: Provided stream URL is empty.")
            return

        if not self.is_valid_url(stream_url):
            print(f"Blocked non-HTTP(S) or malformed URL: {stream_url}")
            return

        # Strict check for HTTPS format
        if URL_REGEX_HTTPS.match(stream_url):
            # It's a valid HTTPS URL
            pass
        elif URL_REGEX_HTTP.match(stream_url):
            # It's an HTTP URL (less secure)
            pass
        else:
            print(f"Blocked non-HTTP(S) or malformed URL: {stream_url}")
            return

        if self._current_url == stream_url:
            # If we're already on this station, resume
            print(f"Resuming existing stream: {stream_url}")
            self._player.play()
            return

        self._current_url = stream_url

        try:
            media = vlc.Media(stream_url)
            self._player.set_media(media)
            self._player.play()
            print(f"Started playing: {stream_url}")
        except Exception as e:
            print(f"Error occurred while trying to play {stream_url}: {e}")

    def stop_station(self):
        """
        Stop playback completely.
        If there's no active media, VLC's stop won't do much, but it doesn't hurt to call it.
        """
        if self._player.is_playing():
            print(f"Stopping current stream: {self._current_url}")
        else:
            print("stop_station called, but nothing is playing.")
        self._player.stop()

    def set_volume(self, volume: int):
        """
        Set the player's volume. VLC volume typically ranges from 0 to 100.
        You can clamp the value if you want to enforce strict bounds.
        """
        # Enforce 0–100 range
        clamped_volume = max(0, min(volume, 100))

        try:
            current_volume = self._player.audio_get_volume()
            self._player.audio_set_volume(clamped_volume)
            print(f"Volume changed from {current_volume} to {clamped_volume}.")
        except Exception as e:
            print(f"Error occurred while setting volume to {volume}: {e}")

    def update_stations(self, stations):
        """
        Update the list of stations.
        """
        self._stations = stations or []
        print(f"Updated stations: {len(self._stations)} stations available.")

    def play_next_station(self):
        """
        Play the next station in the list.
        """
        if not self._stations:
            print("No stations available to play.")
            return
        current_index = next(
            (i for i, s in enumerate(self._stations) if s.get("url") == self._current_url), -1
        )
        next_index = (current_index + 1) % len(self._stations)
        next_station = self._stations[next_index]
        self.play_station(next_station["url"])
        print(f"Playing next station: {next_station['name']}")

    def play_previous_station(self):
        """
        Play the previous station in the list.
        """
        if not self._stations:
            print("No stations available to play.")
            return
        current_index = next(
            (i for i, s in enumerate(self._stations) if s.get("url") == self._current_url), -1
        )
        previous_index = (current_index - 1) % len(self._stations)
        previous_station = self._stations[previous_index]
        self.play_station(previous_station["url"])
        print(f"Playing previous station: {previous_station['name']}")

    def is_playing(self):
        """
        Check if the VLC player is currently playing.
        """
        return self._player.is_playing() == 1  # VLC returns 1 if playing, 0 otherwise