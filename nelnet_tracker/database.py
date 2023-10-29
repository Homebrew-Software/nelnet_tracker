"""Marshals data into a SQLite database."""

import os
from pathlib import Path
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
            scrape_timestamp TEXT NOT NULL,
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
            name TEXT NOT NULL
        )
        """
    )

    # Loan table for reference in many records.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan (
            group_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            group_position INTEGER NOT NULL
        )
        """
    )

    # Group-level data per record.
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS group_record (
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
            main_record_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            current_amount_due TEXT NOT NULL,
            due_date TEXT NOT NULL,
            interest_rate TEXT NOT NULL,
            last_payment_received TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS balance_information (
            main_record_id INTEGER NOT NULL,
            group_id INTEGER NOT NULL,
            principal_balance TEXT NOT NULL,
            accrued_interest TEXT NOT NULL,
            fees TEXT NOT NULL,
            outstanding_balance TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_record (
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
            main_record_id INTEGER NOT NULL,
            loan_id INTEGER NOT NULL,
            convert_to_repayment TEXT NOT NULL,
            original_loan_amount TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_disbursements (
            loan_historic_information_id INTEGER NOT NULL,
            disbursement_info TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS loan_benefit_details (
            main_record_id INTEGER NOT NULL,
            loan_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
    )

    con.commit()


def delete_database() -> None:
    """Removes the database from the file system. Warning: This cannot be
    undone.
    """
    os.remove(CONFIG.database_path)
