from pathlib import Path

def create_full_report(output_root: Path):
    report_dir = output_root / "report"
    report_dir.mkdir(exist_ok=True)

    html = """
    <html>
    <head><meta charset="utf-8"><title>Image Report</title></head>
    <body>
    <h1>Image Clean Report</h1>
    <ul>
        <li>중복 이미지: duplicates/</li>
        <li>유사 이미지: similar/</li>
        <li>해상도 정리: sorted_resolution/</li>
        <li>확장자 정리: sorted_ext/</li>
        <li>날짜 정리: sorted_date/</li>
    </ul>
    </body>
    </html>
    """

    with open(report_dir / "summary.html", "w", encoding="utf-8") as f:
        f.write(html)
