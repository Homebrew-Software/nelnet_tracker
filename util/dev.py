"""Heavy-handed utilities for developers. Handle with care. Make sure you back
up your database before running any of these (nice with SQLite, since you can
simply copy the database like a file).

Most of these were written for a very specific purpose. They can be adapted for
future needs or just kept around for posterity.
"""

import sqlite3

from nelnet_tracker.config import CONFIG


###############################################################################
# DATABASE UPDATE 1
###############################################################################


def add_columns_for_amount_past_due():
    print("Opening connection")
    con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
    cur: sqlite3.Cursor = con.cursor()

    print("Executing ALTER TABLE statements")
    cur.execute(
        """
        ALTER TABLE main_record
        ADD COLUMN past_due_amount TEXT NOT NULL DEFAULT ''
        """
    )
    cur.execute(
        """
        ALTER TABLE main_record
        ADD COLUMN monthly_payment_remaining TEXT NOT NULL DEFAULT ''
        """
    )

    print("Committing")
    con.commit()
    print("Closing")
    con.close()

    print("Done!")


def update_last_main_record(values: dict[str, str]):
    print("Opening connection")
    con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
    cur: sqlite3.Cursor = con.cursor()

    print("Executing UPDATE statements")
    cur.execute(
        """
        UPDATE main_record
        SET current_amount_due = :current_amount_due,
            due_date = :due_date,
            past_due_amount = :past_due_amount,
            monthly_payment_remaining = :monthly_payment_remaining
        WHERE row_id = 8
        """,
        values,
    )

    print("Committing")
    con.commit()
    print("Closing")
    con.close()

    print("Done!")


def reorder_columns_for_amount_past_due():
    print("Opening connection")
    con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
    cur: sqlite3.Cursor = con.cursor()

    print("Creating new table")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS main_record_new (
            row_id INTEGER PRIMARY KEY,
            scrape_timestamp TEXT NOT NULL,
            past_due_amount TEXT NOT NULL,
            monthly_payment_remaining TEXT NOT NULL,
            current_amount_due TEXT NOT NULL,
            due_date TEXT NOT NULL,
            current_balance TEXT NOT NULL,
            last_payment_received TEXT NOT NULL
        )
        """
    )

    print("Transferring data to new table")
    data_rows = list(cur.execute("SELECT * FROM main_record"))
    for row in data_rows:
        cur.execute(
            """
            INSERT INTO main_record_new
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row[0],
                row[1],
                row[6],
                row[7],
                row[2],
                row[3],
                row[4],
                row[5],
            ),
        )

    print("Dropping old table")
    cur.execute("DROP TABLE main_record")

    print("Renaming new table")
    cur.execute("ALTER TABLE main_record_new RENAME TO main_record")

    print("Committing")
    con.commit()

    print("Closing")
    con.close()

    print("Done!")


###############################################################################
# DATABASE UPDATE 2
###############################################################################


def add_column_for_regular_monthly_payment_amount():
    print("Opening connection")
    con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
    cur: sqlite3.Cursor = con.cursor()

    print("Executing ALTER TABLE statements")
    cur.execute(
        """
        ALTER TABLE payment_information
        ADD COLUMN regular_monthly_payment_amount TEXT NOT NULL DEFAULT ''
        """
    )

    print("Committing")
    con.commit()
    print("Closing")
    con.close()

    print("Done!")


def reorder_columns_for_regular_monthly_payment_amount():
    print("Opening connection")
    con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
    cur: sqlite3.Cursor = con.cursor()

    print("Creating new table")
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_information_new (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            current_amount_due TEXT NOT NULL,
            due_date TEXT NOT NULL,
            interest_rate TEXT NOT NULL,
            regular_monthly_payment_amount TEXT NOT NULL,
            last_payment_received TEXT NOT NULL
        )
        """
    )

    print("Transferring data to new table")
    data_rows = list(cur.execute("SELECT * FROM payment_information"))
    for row in data_rows:
        cur.execute(
            """
            INSERT INTO payment_information_new
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                row[0],
                row[1],
                row[2],
                row[3],
                row[4],
                row[5],
                row[7],
                row[6],
            ),
        )

    print("Dropping old table")
    cur.execute("DROP TABLE payment_information")

    print("Renaming new table")
    cur.execute("ALTER TABLE payment_information_new RENAME TO payment_information")

    print("Committing")
    con.commit()

    print("Closing")
    con.close()

    print("Done!")
