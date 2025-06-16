class ReportCreator:
    
    def __init__(self):
        print("We are in ReportCreator")
        pass

    def generate_html_weather_report(self, data, threshold=3.0, output_file="reports/weather_report.html"):
        discrepancies = []
        diffs = []

        for entry in data:
            city = entry["city"]
            web_temp = entry["temperature_web"]
            api_temp = entry["temperature_api"]
            diff = abs(web_temp - api_temp)
            

            diffs.append(diff)

            if diff > threshold:
                discrepancies.append((city, web_temp, api_temp, diff))

        mean_diff = sum(diffs) / len(diffs) if diffs else 0
        max_diff = max(diffs) if diffs else 0
        min_diff = min(diffs) if diffs else 0

        html = f"""
        <html>
        <head>
            <title>Weather Discrepancy Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; background-color: #f9f9f9; color: #333; }}
                table {{ border-collapse: collapse; width: 80%; margin: 20px auto; }}
                th, td {{ border: 1px solid #ccc; padding: 8px; text-align: center; }}
                th {{ background-color: #444; color: white; }}
                h2, p {{ text-align: center; }}
            </style>
        </head>
        <body>
            <h2>Weather Discrepancy Report</h2>
            <p>Threshold: {threshold}°C</p>
            <table>
                <tr>
                    <th>City</th>
                    <th>Website Temp (°C)</th>
                    <th>API Temp (°C)</th>
                    <th>Difference (°C)</th>
                </tr>"""

        for city, web, api, diff in discrepancies:
            html += f"""
                <tr>
                    <td>{city}</td>
                    <td>{web}</td>
                    <td>{api}</td>
                    <td>{round(diff, 2)}</td>
                </tr>"""

        html += f"""
            </table>
            <h3 style="text-align: center;">Summary Statistics</h3>
            <p>Mean Discrepancy: {round(mean_diff, 2)}°C</p>
            <p>Max Discrepancy: {round(max_diff, 2)}°C</p>
            <p>Min Discrepancy: {round(min_diff, 2)}°C</p>
        </body>
        </html>
        """

        with open(output_file, "w", encoding="utf-8") as f:
            f.write(html)

        print("Reported created")