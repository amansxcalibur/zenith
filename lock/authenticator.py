import pam
import threading
from loguru import logger

from gi.repository import GLib # type: ignore

class Authenticator:
    def __init__(self, username: str):
        self.username = username
        self._authenticating = False

    def authenticate(self, password: str, callback):
        """Authenticate in a background thread."""
        if self._authenticating:
            return

        self._authenticating = True

        def auth_thread():
            try:
                success = pam.authenticate(self.username, password)
                if success:
                    GLib.idle_add(callback, True, None)
                else:
                    GLib.idle_add(callback, False, "Incorrect password")
            except Exception as e:
                logger.error(f"PAM authentication error: {e}")
                GLib.idle_add(callback, False, "Authentication error")
            finally:
                self._authenticating = False

        threading.Thread(target=auth_thread, daemon=True).start()

    def is_authenticating(self):
        return self._authenticating