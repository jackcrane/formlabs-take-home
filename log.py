import pathlib
import csv

LOG_FILE = pathlib.Path().resolve() / "print_log.csv"

def write_log(filename):
    # Ensure file exists and determine next ID
    next_id = 1

    if LOG_FILE.exists():
        with open(LOG_FILE, "r", newline="") as f:
            reader = csv.reader(f)
            rows = list(reader)
            if len(rows) > 1:  # has header + data
                try:
                    next_id = int(rows[-1][0]) + 1
                except:
                    next_id = 1

    # Write (append mode)
    file_exists = LOG_FILE.exists()

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        # Write header if new file
        if not file_exists or LOG_FILE.stat().st_size == 0:
            writer.writerow(["Patient ID", "Filename"])

        writer.writerow([next_id, filename])