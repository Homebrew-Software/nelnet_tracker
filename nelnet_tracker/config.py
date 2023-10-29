"""Program configuration."""

from pathlib import Path

import platformdirs


class Config:
    def __init__(self) -> None:
        self.app_name: str = "nelnet_tracker"
        self.app_author: str = "Homebrew-Software"
        self.database_name: str = "nelnet_records.sqlite3"

    @property
    def database_path(self) -> Path:
        return (
            Path(
                platformdirs.user_data_dir(
                    appname=self.app_name, appauthor=self.app_author
                )
            )
            / self.database_name
        )


CONFIG: Config = Config()
