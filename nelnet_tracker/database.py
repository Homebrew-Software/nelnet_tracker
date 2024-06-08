"""Marshals data into a SQLite database."""

import os
import sqlite3

from .config import CONFIG


def create_database() -> None:
    """Creates all the necessary database tables."""
    CONFIG.database_path.parent.mkdir(parents=True, exist_ok=True)

    con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
    cur: sqlite3.Cursor = con.cursor()

    # Top-level record data containing timestamp and high-level data.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS main_record (
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

    # Group table for reference in many records.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_group (
            row_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )

    # Group-level data per record.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS group_record (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            loan_type TEXT NOT NULL,
            status TEXT NOT NULL,
            repayment_plan TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS payment_information (
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

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS balance_information (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            principal_balance TEXT NOT NULL,
            accrued_interest TEXT NOT NULL,
            fees TEXT NOT NULL,
            outstanding_balance TEXT NOT NULL
        )
        """
    )

    # Loan table for reference in many records.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan (
            row_id INTEGER PRIMARY KEY,
            group_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            group_placement INTEGER NOT NULL
        )
        """
    )

    # Loan-level data per record.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_record (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            loan_id INTEGER NOT NULL,
            loan_type TEXT NOT NULL,
            loan_status TEXT NOT NULL,
            interest_subsidy TEXT NOT NULL,
            lender_name TEXT NOT NULL,
            school_name TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_current_information (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            loan_id INTEGER NOT NULL,
            due_date TEXT NOT NULL,
            interest_rate TEXT NOT NULL,
            interest_rate_type TEXT NOT NULL,
            loan_term TEXT NOT NULL,
            principal_balance TEXT NOT NULL,
            accrued_interest TEXT NOT NULL,
            capitalized_interest TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_historic_information (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            loan_id INTEGER NOT NULL,
            convert_to_repayment TEXT NOT NULL,
            original_loan_amount TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_disbursement (
            row_id INTEGER PRIMARY KEY,
            loan_historic_information_id INTEGER NOT NULL,
            info TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_benefit_details (
            row_id INTEGER PRIMARY KEY,
            main_record_id INTEGER NOT NULL,
            loan_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    con.commit()
    con.close()


def delete_database() -> None:
    """Removes the database from the file system. Warning: This cannot be
    undone.
    """
    os.remove(CONFIG.database_path)


class DatabaseRecord:
    """A record to be inserted into the database."""

    def __init__(self, data: dict) -> None:
        self.data: dict = data

    def insert_all(self) -> None:
        """Inserts all data into the database."""
        self.con: sqlite3.Connection = sqlite3.connect(CONFIG.database_path)
        self.cur: sqlite3.Cursor = self.con.cursor()

        self.propagate_blank_row_id()
        main_record_id: int = self.insert_main_record()
        self.propagate_main_record_id(main_record_id)
        for group in self.data["groups"]:
            group_id: int = self.insert_loan_group(group)
            self.propagate_group_id(group_id)
            self.insert_group_record(group)
            self.insert_payment_information(group)
            self.insert_balance_information(group)
            for loan in group["loans"]:
                loan_id: int = self.insert_loan(loan)
                self.propagate_loan_id(loan_id)
                self.insert_loan_record(loan)
                self.insert_loan_current_information(loan)
                historic_info_id: int = self.insert_loan_historic_information(loan)
                self.insert_loan_disbursements(loan, historic_info_id)
                self.insert_loan_benefit_details(loan)

        self.con.commit()
        self.con.close()

    def propagate_blank_row_id(self) -> None:
        """Inserts a None in each section of the data dictionary that will be
        used as data in INSERT statements.
        """
        self.data["row_id"] = None
        for group in self.data["groups"]:
            group["row_id"] = None
            group["payment_information"]["row_id"] = None
            group["balance_information"]["row_id"] = None
            for loan in group["loans"]:
                loan["row_id"] = None
                loan["current_information"]["row_id"] = None
                loan["historic_information"]["row_id"] = None

    def insert_main_record(self) -> int:
        """Inserts the main record data into the database and returns the new
        main record ID.
        """
        self.cur.execute(
            """
            INSERT INTO main_record VALUES (
                :row_id,
                :scrape_timestamp,
                :past_due_amount,
                :monthly_payment_remaining,
                :current_amount_due,
                :due_date,
                :current_balance,
                :last_payment_received
            )
            """,
            self.data,
        )
        row_id: int | None = self.cur.lastrowid
        if row_id is None:
            raise RuntimeError("Didn't get the new main record ID")
        return row_id

    def propagate_main_record_id(self, id_: int) -> None:
        """Propagates the given main record ID into all areas of the data
        dictionary for convenience when using pieces of it as data for SQLite
        INSERT statements.
        """
        for group in self.data["groups"]:
            group["main_record_id"] = id_
            group["payment_information"]["main_record_id"] = id_
            group["balance_information"]["main_record_id"] = id_
            for loan in group["loans"]:
                loan["main_record_id"] = id_
                loan["current_information"]["main_record_id"] = id_
                loan["historic_information"]["main_record_id"] = id_

    def insert_loan_group(self, group: dict) -> int:
        """Inserts the given loan group into the database, if it does not
        exist, and returns the new group ID.
        """
        self.cur.execute("SELECT row_id FROM loan_group WHERE name == :name", group)
        result: tuple | None = self.cur.fetchone()
        if result is None:
            self.cur.execute("INSERT INTO loan_group VALUES (:row_id, :name)", group)
            row_id: int | None = self.cur.lastrowid
            if row_id is None:
                raise RuntimeError("Didn't get the new loan group ID")
            return row_id
        return result[0]

    def propagate_group_id(self, id_: int) -> None:
        """Propagates the given loan group ID into all areas of the data
        dictionary for convenience when using pieces of it as data for SQLite
        INSERT statements.
        """
        for group in self.data["groups"]:
            group["group_id"] = id_
            group["payment_information"]["group_id"] = id_
            group["balance_information"]["group_id"] = id_
            for loan in group["loans"]:
                loan["group_id"] = id_

    def insert_group_record(self, group: dict) -> None:
        self.cur.execute(
            """
            INSERT INTO group_record VALUES (
                :row_id,
                :main_record_id,
                :group_id,
                :loan_type,
                :status,
                :repayment_plan
            )
            """,
            group,
        )

    def insert_payment_information(self, group: dict) -> None:
        self.cur.execute(
            """
            INSERT INTO payment_information VALUES (
                :row_id,
                :main_record_id,
                :group_id,
                :current_amount_due,
                :due_date,
                :interest_rate,
                :regular_monthly_payment_amount,
                :last_payment_received
            )
            """,
            group["payment_information"],
        )

    def insert_balance_information(self, group: dict) -> None:
        self.cur.execute(
            """
            INSERT INTO balance_information VALUES (
                :row_id,
                :main_record_id,
                :group_id,
                :principal_balance,
                :accrued_interest,
                :fees,
                :outstanding_balance
            )
            """,
            group["balance_information"],
        )

    def insert_loan(self, loan: dict) -> int:
        """Inserts the given loan into the database, if it does not exist, and
        returns the new loan ID.
        """
        self.cur.execute("SELECT row_id FROM loan WHERE name == :name", loan)
        result: tuple | None = self.cur.fetchone()
        if result is None:
            self.cur.execute(
                "INSERT INTO loan VALUES (:row_id, :group_id, :name, :group_placement)",
                loan,
            )
            row_id: int | None = self.cur.lastrowid
            if row_id is None:
                raise RuntimeError("Didn't get the new loan ID")
            return row_id
        return result[0]

    def propagate_loan_id(self, id_: int) -> None:
        """Propagates the given loan ID into all areas of the data dictionary
        for convenience when using pieces of it as data for SQLite INSERT
        statements.
        """
        for group in self.data["groups"]:
            for loan in group["loans"]:
                loan["loan_id"] = id_
                loan["current_information"]["loan_id"] = id_
                loan["historic_information"]["loan_id"] = id_

    def insert_loan_record(self, loan: dict) -> None:
        self.cur.execute(
            """
            INSERT INTO loan_record VALUES (
                :row_id,
                :main_record_id,
                :loan_id,
                :loan_type,
                :loan_status,
                :interest_subsidy,
                :lender_name,
                :school_name
            )
            """,
            loan,
        )

    def insert_loan_current_information(self, loan: dict) -> None:
        self.cur.execute(
            """
            INSERT INTO loan_current_information VALUES (
                :row_id,
                :main_record_id,
                :loan_id,
                :due_date,
                :interest_rate,
                :interest_rate_type,
                :loan_term,
                :principal_balance,
                :accrued_interest,
                :capitalized_interest
            )
            """,
            loan["current_information"],
        )

    def insert_loan_historic_information(self, loan: dict) -> int:
        """Inserts historic information for the given loan into the database
        and returns the new loan historic information ID.
        """
        self.cur.execute(
            """
            INSERT INTO loan_historic_information VALUES (
                :row_id,
                :main_record_id,
                :loan_id,
                :convert_to_repayment,
                :original_loan_amount
            )
            """,
            loan["historic_information"],
        )
        row_id: int | None = self.cur.lastrowid
        if row_id is None:
            raise RuntimeError("Didn't get the new historic information ID")
        return row_id

    def insert_loan_disbursements(self, loan: dict, historic_info_id: int) -> None:
        for disbursement in loan["historic_information"]["disbursements"]:
            self.cur.execute(
                """
                INSERT INTO loan_disbursement VALUES (
                    :row_id,
                    :loan_historic_information_id,
                    :info
                )
                """,
                dict(
                    row_id=None,
                    loan_historic_information_id=historic_info_id,
                    info=disbursement,
                ),
            )

    def insert_loan_benefit_details(self, loan: dict) -> None:
        for benefit in loan["benefit_details"]:
            self.cur.execute(
                """
                INSERT INTO loan_benefit_details VALUES (
                    :row_id,
                    :main_record_id,
                    :loan_id,
                    :name,
                    :status
                )
                """,
                dict(
                    row_id=None,
                    main_record_id=loan["main_record_id"],
                    loan_id=loan["loan_id"],
                    name=benefit[0],
                    status=benefit[1],
                ),
            )


def write_record_to_database(data: dict) -> None:
    """Inserts a record entry into the database."""
    record: DatabaseRecord = DatabaseRecord(data)
    record.insert_all()


def select_all_balances() -> list[tuple[str, str]]:
    """Returns all associated timestamps and aggregate balances."""
    con = sqlite3.connect(CONFIG.database_path)
    with con:
        result: list[tuple[str, str]] = con.execute(
            "SELECT scrape_timestamp, current_balance FROM main_record"
        ).fetchall()
    return result
