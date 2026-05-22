from __future__ import annotations

import argparse
import sys
from pathlib import Path

from analyze_round_summary import generate_chart_rows, generate_report, write_chart_csv
from summarize_evidence_rounds import summarize_packages, write_csv, _candidate_zip_paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Build LifeReflexArc pre-experiment summary artifacts from evidence-package ZIPs: "
            "round-summary.csv, round-analysis.md, and round-chart-data.csv."
        ),
    )
    parser.add_argument("paths", nargs="+", help="Evidence ZIP file, directory, or glob pattern")
    parser.add_argument(
        "-o",
        "--output-dir",
        default="output/pre-experiment-analysis",
        help="Directory for generated CSV and Markdown files.",
    )
    parser.add_argument("--summary-name", default="round-summary.csv", help="Generated summary CSV file name.")
    parser.add_argument("--report-name", default="round-analysis.md", help="Generated Markdown analysis file name.")
    parser.add_argument("--chart-name", default="round-chart-data.csv", help="Generated PPT/Excel chart-data CSV file name.")
    parser.add_argument("--recursive", action="store_true", help="When a directory is passed, scan ZIPs recursively.")
    parser.add_argument(
        "--include-invalid",
        action="store_true",
        help="Include invalid packages as FAILED rows instead of aborting.",
    )
    args = parser.parse_args(argv)

    paths = _candidate_zip_paths(args.paths, recursive=args.recursive)
    if not paths:
        print("FAILED: no ZIP packages matched the given input paths.", file=sys.stderr)
        return 1

    try:
        fieldnames, rows = summarize_packages(paths, include_invalid=args.include_invalid)
        output_dir = Path(args.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        summary_path = output_dir / args.summary_name
        report_path = output_dir / args.report_name
        chart_path = output_dir / args.chart_name
        write_csv(fieldnames, rows, summary_path)
        report = generate_report(rows, source_name=str(summary_path))
        report_path.write_text(report, encoding="utf-8")
        write_chart_csv(generate_chart_rows(rows), chart_path)
    except (OSError, ValueError) as exc:
        print(f"FAILED: {exc}", file=sys.stderr)
        return 1

    print(f"OK: summarized {len(rows)} evidence round(s) from {len(paths)} package(s)")
    print(f"- CSV: {summary_path}")
    print(f"- Markdown: {report_path}")
    print(f"- Chart CSV: {chart_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
