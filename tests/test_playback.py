import unittest
from unittest.mock import ANY, MagicMock, patch

import web_app


class PlaybackTests(unittest.TestCase):
    def tearDown(self) -> None:
        web_app.PLAYBACK_PROCESS = None

    @patch("web_app.threading.Thread")
    @patch("web_app.subprocess.Popen")
    def test_new_preview_stops_audio_already_playing(self, popen: MagicMock, thread: MagicMock) -> None:
        previous = MagicMock()
        previous.poll.return_value = None
        replacement = MagicMock()
        popen.return_value = replacement
        web_app.PLAYBACK_PROCESS = previous

        web_app.start_playback(["say", "replacement"])

        previous.terminate.assert_called_once_with()
        popen.assert_called_once_with(
            ["say", "replacement"],
            stdout=web_app.subprocess.DEVNULL,
            stderr=web_app.subprocess.DEVNULL,
        )
        self.assertIs(web_app.PLAYBACK_PROCESS, replacement)
        thread.assert_called_once_with(target=ANY, daemon=True)
        thread.return_value.start.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
