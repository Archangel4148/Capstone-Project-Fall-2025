from api.database_service import DatabaseService
import dataclasses
import itertools
import time

@dataclasses.dataclass
class AppTimestamp:
    path: str
    query_timestamp: int

class App():
    def __init__(self, path: str, timestamps: list[int]=list()) -> None:
        self._path: str = path
        self._timestamps: list[int] = timestamps

        self._api = ScreenTimeAPI()

    def get_path(self) -> str:
        return self._path

    def get_timestamps(self) -> list[int]:
        return self._timestamps

    def _add_timestamp(self, timestamp: int) -> None:
        self._api.add_entry(AppTimestamp(self._path, timestamp))
        self._timestamps.append(timestamp)

    def add_timestamps(self, timestamps: list[int]) -> None:
        for t in timestamps:
            self._add_timestamp(t)

    def get_usage_percent(self) -> None:
        return len(self._timestamps) / time.time()

class ScreenTimeAPI:
    def get_application_usage(self, query_end_time=0) -> list[App]:
        apps = list()
        query_end_time = str(query_end_time)

        paths = DatabaseService.select(
            "screen_time",
            ["application_path"],
            [("query_timestamp", ">", query_end_time)]
        )
        paths = {p[0] for p in paths}

        for p in paths:
            timestamps = DatabaseService.select(
                "screen_time",
                ["query_timestamp"],
                [
                    ("query_timestamp", ">", query_end_time),
                    ("application_path", "=", p)
                ]
            )
            timestamps = [t[0] for t in timestamps]
            print(timestamps)

            apps.append(App(p, timestamps))

        return apps

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
