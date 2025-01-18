from pynput.keyboard import Key, Listener
import threading

class MediaKeyListener:
    """
    A class to listen to media keys and control playback.
    """

    def __init__(self, radio_player):
        self.radio_player = radio_player
        self.listener_thread = threading.Thread(target=self._start_listener)
        self.listener_thread.daemon = True

    def _on_press(self, key):
        try:
            if key == Key.media_play_pause:
                print("Play/Pause button pressed.")
                if self.radio_player.is_playing():
                    self.radio_player.stop_station()
                else:
                    self.radio_player.play_station(self.radio_player._current_url)
            elif key == Key.media_next:
                print("Next button pressed.")
                self.radio_player.play_next_station()
            elif key == Key.media_previous:
                print("Previous button pressed.")
                self.radio_player.play_previous_station()
        except Exception as e:
            print(f"Error handling key press: {e}")

    def _start_listener(self):
        with Listener(on_press=self._on_press) as listener:
            listener.join()

    def start(self):
        """
        Start the media key listener.
        """
        self.listener_thread.start()
