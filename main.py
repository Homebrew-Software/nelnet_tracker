"""The main script. Useful for debugging."""

from nelnet_tracker.cli import scrape

if __name__ == "__main__":
    scrape(["--json", "~/nelnet_data.json"])

    print("done")
