from pathlib import Path
from datetime import datetime


def generate_html_report(output_path: Path, summary: dict, logs: list[str]):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    html = f"""
<html>
<head>
<meta charset="UTF-8">
<title>이미지 정리 리포트</title>
<style>
body {{
    background: #1e1e1e;
    color: #e5e5e5;
    font-family: Consolas, monospace;
    padding: 20px;
}}
h1 {{ color: #90caf9; }}
.card {{
    background: #2b2b2b;
    padding: 15px;
    margin-bottom: 20px;
    border-radius: 8px;
}}
.log {{
    white-space: pre-wrap;
    background: #111;
    padding: 10px;
    border-radius: 5px;
    font-size: 14px;
}}
</style>
</head>
<body>
<h1>📄 이미지 정리 리포트</h1>
<p>생성 시간: {datetime.now()}</p>

<div class="card">
<h2>요약</h2>
<ul>
{''.join(f"<li><b>{k}</b>: {v}</li>" for k, v in summary.items())}
</ul>
</div>

<div class="card">
<h2>상세 로그</h2>
<div class="log">
{''.join(line + "<br>" for line in logs)}
</div>
</div>

</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    return output_path
