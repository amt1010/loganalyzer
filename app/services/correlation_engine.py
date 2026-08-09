def analyze_logs(logs):
    origin_ok = any("Origin returned 200" in l for l in logs)
    cdn_404 = any("CDN returned 404" in l for l in logs)

    if origin_ok and cdn_404:
        return "Soft 404 (CDN cache issue)"

    if cdn_404:
        return "Hard 404"

    return "No issue detected"