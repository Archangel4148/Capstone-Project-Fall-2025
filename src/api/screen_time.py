from api.database_service import DatabaseService
import dataclasses

@dataclasses.dataclass
class App:
    path: str
    query_timestamp: int

class ScreenTimeAPI:
    def get_application_usage(self, query_end_time=0) -> list[App]:
        query_end_time = str(query_end_time)

        rows = DatabaseService.select("screen_time", conditions=[("query_timestamp", ">", query_end_time)])
        app_usage = [App(*row) for row in rows]

        return app_usage

    def delete_after_date(self, end_time=0) -> None:
        end_time = str(end_time)
        DatabaseService.delete("screen_time", conditions=[("query_timestamp", "<", end_time)])

    def remove_app(self, path: str) -> None:
        DatabaseService.delete("screen_time", conditions=[("application_path", "=", path)])

    def add_entry(self, app: App):
        DatabaseService.insert("screen_time", values={"application_path": app.path, "query_timestamp": app.query_timestamp})
