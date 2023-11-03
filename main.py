"""The main script. Useful for debugging."""

if __name__ == "__main__":
    from nelnet_tracker.database import delete_database

    delete_database()

    # from nelnet_tracker.database import create_database

    # create_database()

    # import json
    # from pathlib import Path
    # from nelnet_tracker.database import write_record_to_database

    # with open(Path.home() / "nelnet_scrape.json", "r") as jf:
    #     data: dict = json.load(jf)

    # write_record_to_database(data)

    # import sqlite3
    # from nelnet_tracker.config import CONFIG

    # con = sqlite3.connect(CONFIG.database_path)
    # with con:
    #     con.execute(
    #         "INSERT INTO loan_group VALUES (:id, :name)",
    #         dict(
    #             id=None,
    #             name="what",
    #         ),
    #     )
    #     # result = con.execute("SELECT id FROM loan_group").fetchall()
    # # print(result)
