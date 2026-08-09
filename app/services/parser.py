import re

def parse_log_line(line):
    return {
        "url": extract_url(line),
        "user": extract_user(line),
        "timestamp": extract_timestamp(line),
        "status": extract_status(line),
        "log_level": extract_log_level(line),
        "is_noidahealth": "noidahealth" in line.lower(),
        "is_publish": detect_publish(line),
        "raw": line
    }


def extract_url(line):
    match = re.search(r"https?://[^\s\"']+", line)
    if match:
        return match.group(0)

    match = re.search(r"(\/[^\s]+)", line)
    return match.group(1) if match else None


def extract_user(line):
    # Sitecore audit format
    match = re.search(r"AUDIT\s+\(sitecore\\([^)]+)\)", line)
    if match:
        return match.group(1)

    # fallback
    match = re.search(r"user:\s*(\w+)", line)
    return match.group(1) if match else "unknown"


def extract_timestamp(line):
    match = re.search(r"\d{2} \w{3} \d{4} \d{2}:\d{2}:\d{2}", line)
    return match.group(0) if match else None


def extract_status(line):
    match = re.search(r"\b(200|404|500|301|302)\b", line)
    return int(match.group(1)) if match else None


def extract_log_level(line):
    match = re.search(r"\b(INFO|WARN|ERROR|DEBUG|FATAL)\b", line)
    return match.group(1) if match else "UNKNOWN"


def detect_publish(line):
    return "AUDIT" in line and "sitecore\\" in line