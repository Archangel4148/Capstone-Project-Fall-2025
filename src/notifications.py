from notifypy import Notify


class NotificationManager:
    _app_name = "Nudgy"

    @classmethod
    def notify(cls, title: str, message: str):
        """Send a desktop notification with the provided title and message"""
        n = Notify()
        n.application_name = cls._app_name
        n.title = title
        n.message = message
        n.send()
