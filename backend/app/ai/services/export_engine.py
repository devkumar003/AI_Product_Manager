"""
Task 23 — AI Export Engine

Exports AI-generated content to multiple formats:
Markdown, JSON, CSV, HTML, and presentation-ready structures.
PDF/DOCX generation is architecture-ready (requires optional dependencies).
"""

import csv
import io
import json
import logging
from typing import Any

logger = logging.getLogger("app.ai.services.export")


class ExportEngine:
    """Converts structured AI outputs into exportable document formats."""

    # ── Markdown ──

    @staticmethod
    def to_markdown(data: dict[str, Any], title: str = "AI ProductOS Export") -> str:
        lines = [f"# {title}\n"]

        for key, value in data.items():
            heading = key.replace("_", " ").title()
            lines.append(f"\n## {heading}\n")

            if isinstance(value, str):
                lines.append(value + "\n")
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        lines.append(f"- **{item.get('title', item.get('name', ''))}**")
                        for k, v in item.items():
                            if k not in ("title", "name"):
                                lines.append(f"  - {k}: {v}")
                    else:
                        lines.append(f"- {item}")
                lines.append("")
            elif isinstance(value, dict):
                for k, v in value.items():
                    lines.append(f"- **{k}**: {v}")
                lines.append("")
            else:
                lines.append(str(value) + "\n")

        return "\n".join(lines)

    # ── JSON ──

    @staticmethod
    def to_json(data: dict[str, Any], indent: int = 2) -> str:
        return json.dumps(data, indent=indent, default=str)

    # ── CSV ──

    @staticmethod
    def to_csv(data: list[dict[str, Any]]) -> str:
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        for row in data:
            writer.writerow({k: str(v) for k, v in row.items()})
        return output.getvalue()

    # ── HTML ──

    @staticmethod
    def to_html(data: dict[str, Any], title: str = "AI ProductOS Export") -> str:
        html = [
            "<!DOCTYPE html>",
            "<html lang='en'><head><meta charset='UTF-8'>",
            f"<title>{title}</title>",
            "<style>",
            "body { font-family: 'Inter', sans-serif; max-width: 900px; margin: 40px auto; "
            "padding: 20px; color: #1a1a2e; line-height: 1.7; }",
            "h1 { color: #16213e; border-bottom: 3px solid #0f3460; padding-bottom: 10px; }",
            "h2 { color: #0f3460; margin-top: 30px; }",
            "table { width: 100%; border-collapse: collapse; margin: 16px 0; }",
            "th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }",
            "th { background: #0f3460; color: white; }",
            "ul { padding-left: 20px; }",
            ".badge { display: inline-block; padding: 2px 10px; border-radius: 12px; "
            "background: #e2e8f0; font-size: 12px; margin: 2px; }",
            "</style></head><body>",
            f"<h1>{title}</h1>",
        ]

        for key, value in data.items():
            heading = key.replace("_", " ").title()
            html.append(f"<h2>{heading}</h2>")

            if isinstance(value, str):
                html.append(f"<p>{value}</p>")
            elif isinstance(value, list):
                if value and isinstance(value[0], dict):
                    headers = list(value[0].keys())
                    html.append(
                        "<table><tr>"
                        + "".join(f"<th>{h}</th>" for h in headers)
                        + "</tr>"
                    )
                    for item in value:
                        html.append(
                            "<tr>"
                            + "".join(f"<td>{item.get(h, '')}</td>" for h in headers)
                            + "</tr>"
                        )
                    html.append("</table>")
                else:
                    html.append(
                        "<ul>" + "".join(f"<li>{item}</li>" for item in value) + "</ul>"
                    )
            elif isinstance(value, dict):
                html.append("<ul>")
                for k, v in value.items():
                    html.append(f"<li><strong>{k}:</strong> {v}</li>")
                html.append("</ul>")
            else:
                html.append(f"<p>{value}</p>")

        html.append("</body></html>")
        return "\n".join(html)

    # ── Presentation-Ready Structure ──

    @staticmethod
    def to_presentation(
        data: dict[str, Any], title: str = "AI ProductOS"
    ) -> list[dict[str, Any]]:
        """Convert to a slide-by-slide structure for rendering or export."""
        slides = [
            {
                "slide": 1,
                "title": title,
                "content": "AI-Powered Product Intelligence",
                "type": "title",
            }
        ]
        slide_num = 2

        for key, value in data.items():
            heading = key.replace("_", " ").title()
            if isinstance(value, str):
                bullets = [value]
            elif isinstance(value, list):
                bullets = [
                    (
                        str(item)
                        if not isinstance(item, dict)
                        else item.get("title", str(item))
                    )
                    for item in value[:8]
                ]
            elif isinstance(value, dict):
                bullets = [f"{k}: {v}" for k, v in list(value.items())[:8]]
            else:
                bullets = [str(value)]

            slides.append(
                {
                    "slide": slide_num,
                    "title": heading,
                    "bullets": bullets,
                    "type": "content",
                }
            )
            slide_num += 1

        return slides

    # ── PDF (Architecture-ready) ──

    @staticmethod
    def to_pdf_ready(data: dict[str, Any], title: str = "Export") -> dict[str, Any]:
        """
        Returns a structure ready for PDF generation.
        Actual PDF rendering requires reportlab or weasyprint (future dependency).
        """
        return {
            "format": "pdf",
            "title": title,
            "sections": [
                {"heading": k.replace("_", " ").title(), "body": v}
                for k, v in data.items()
            ],
            "status": "ready_for_rendering",
            "renderer": "reportlab or weasyprint (install separately)",
        }

    # ── DOCX (Architecture-ready) ──

    @staticmethod
    def to_docx_ready(data: dict[str, Any], title: str = "Export") -> dict[str, Any]:
        """
        Returns a structure ready for DOCX generation.
        Actual DOCX rendering requires python-docx (future dependency).
        """
        return {
            "format": "docx",
            "title": title,
            "sections": [
                {"heading": k.replace("_", " ").title(), "body": v}
                for k, v in data.items()
            ],
            "status": "ready_for_rendering",
            "renderer": "python-docx (install separately)",
        }
