from api.database_service import DatabaseService
import dataclasses

@dataclasses.dataclass
class AppTimestamp:
    path: str
    query_timestamp: int

class ScreenTimeAPI:
    def get_application_usage(self, query_end_time=0) -> list[AppTimestamp]:
        query_end_time = str(query_end_time)

        rows = DatabaseService.select(
            "screen_time",
            ["application_path", "query_timestamp"],
            [("query_timestamp", ">", query_end_time)]
        )
        app_usage = [AppTimestamp(*row) for row in rows]

        return app_usage

    def delete_after_date(self, end_time=0) -> None:
        end_time = str(end_time)
        DatabaseService.delete("screen_time", conditions=[("query_timestamp", "<", end_time)])

    def remove_app(self, path: str) -> None:
        DatabaseService.delete("screen_time", conditions=[("application_path", "=", path)])

    def add_entry(self, app: AppTimestamp):
        DatabaseService.insert("screen_time", values={"application_path": app.path, "query_timestamp": app.query_timestamp})

    def get_usage_percentages(self, apps: list[AppTimestamp]) -> dict[str, float]:
        usage = dict()

        for a in apps:
            try:
                usage[a] += 1
            except KeyError:
                usage[a] = 1

        for u in usage:
            u /= len(apps)

        usage = {k: usage[k] for k in sorted(usage)}


    #     return usage
