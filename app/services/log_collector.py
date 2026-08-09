import os
from app.services.parser import parse_log_line

def collect_logs(url):
    parsed_logs = []

    for file in os.listdir("data/logs"):
        file_path = os.path.join("data/logs", file)

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    if url in line:
                        parsed = parse_log_line(line)
                        parsed_logs.append(parsed)
        except Exception as e:
            print("Error reading:", file, e)

    return parsed_logs