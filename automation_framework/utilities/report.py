from ..utilities.db_helpers import DatabaseHelper

def generate_report():
    TEMP_DISCREPANCY_THRESHOLD = 2.0
    REPORT_PATH = "reports/report.md"
    rows = DatabaseHelper().get_weather_data_of_all_cities()
    discrepancies = []
    diffs = []

    for row in rows:
        city, temp_web, feels_like_web, temp_api, feels_like_api, avg = row
        diff = abs(temp_web - temp_api)
        diffs.append(diff)
        if diff > TEMP_DISCREPANCY_THRESHOLD:
            discrepancies.append((city, temp_web, temp_api, diff))

    with open(REPORT_PATH, "w") as f:
        f.write("# Temperature Discrepancy Report\n\n")
        f.write(f"## Cities with > {TEMP_DISCREPANCY_THRESHOLD}C discrepancy\n\n")
        for city, temp_web, temp_api, diff in discrepancies:
            f.write(f"- {city}: Web={temp_web}C, API={temp_api}C, Diff={diff:.2f}C\n")
        f.write("\n## Summary Statistics\n")
        f.write(f"- Mean discrepancy: {sum(diffs)/len(diffs):.2f}C\n")
        f.write(f"- Max discrepancy: {max(diffs):.2f}C\n")
        f.write(f"- Min discrepancy: {min(diffs):.2f}C\n")