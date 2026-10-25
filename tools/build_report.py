"""Build a shareable Allure report without local host/process metadata."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "artifacts/allure-results"
OUTPUT = ROOT / "artifacts/allure-report"


def sanitize_results():
    files = list(RESULTS.glob("*-result.json"))
    if not files:
        raise SystemExit("Нет результатов Allure. Сначала запустите Pytest.")
    for path in files:
        result = json.loads(path.read_text(encoding="utf-8"))
        result["labels"] = [
            label for label in result.get("labels", [])
            if label.get("name") not in {"host", "thread"}
        ]
        path.write_text(json.dumps(result, ensure_ascii=False), encoding="utf-8")
    return len(files)


def sanitize_junit():
    for directory in (ROOT / "artifacts", ROOT / "verification"):
        for path in directory.glob("*.xml"):
            tree = ET.parse(path)
            changed = False
            for node in tree.iter():
                if "hostname" in node.attrib:
                    del node.attrib["hostname"]
                    changed = True
            if changed:
                tree.write(path, encoding="utf-8", xml_declaration=True)


def remove_analytics(path):
    html = path.read_text(encoding="utf-8")

    def keep_script(match):
        attrs, body = match.groups()
        if "googletagmanager.com/gtag/" in attrs:
            return ""
        if re.match(r"\s*window\.dataLayer\s*=", body):
            return ""
        return match.group(0)

    html = re.sub(r"<script\b([^>]*)>(.*?)</script>", keep_script, html, flags=re.S)
    path.write_text(html, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sanitize-only", action="store_true")
    args = parser.parse_args()
    count = sanitize_results()
    sanitize_junit()
    print(f"Убраны метки host/thread из {count} результатов и hostname из JUnit.", flush=True)
    if args.sanitize_only:
        return
    cli = ROOT / "node_modules/.bin/allure"
    subprocess.run(
        [str(cli), "awesome", "--single-file", "--output", str(OUTPUT), str(RESULTS)],
        cwd=ROOT,
        check=True,
    )
    remove_analytics(OUTPUT / "index.html")
    print(f"Отчёт без внешней аналитики: {OUTPUT / 'index.html'}")


if __name__ == "__main__":
    main()
