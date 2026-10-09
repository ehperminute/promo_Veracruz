#!/usr/bin/env python3
"""Convert a Markdown report to a printable PDF using Pandoc and WeasyPrint.

Dependencies (no extra Python packages):
  - Pandoc: https://pandoc.org/installing.html
  - WeasyPrint: python -m pip install weasyprint

From repository root:
  python scripts/reporting/export_markdown_pdf.py docs/RESUMEN_DATOS.md
  python scripts/reporting/export_markdown_pdf.py docs/DATA_SUMMARY.md --portrait
  python scripts/reporting/export_markdown_pdf.py docs/RESUMEN_DATOS.md --refresh

The --refresh option regenerates the report with the repository's existing
scripts/reporting/build_data_summary.py before converting.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


CSS = r"""
@page { size: A4 landscape; margin: 14mm 14mm 16mm 14mm; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  color: #162737; background: #fff;
  font-family: Arial, 'Noto Sans', sans-serif;
  font-size: 10pt; line-height: 1.36;
}
h1 { font-size: 22pt; color: #153a5a; margin: 0 0 9mm; }
h2 { font-size: 15pt; color: #153a5a; padding-bottom: 2mm;
     border-bottom: 1px solid #adc3d5; margin: 8mm 0 4mm;
     break-after: avoid; }
h3 { font-size: 11.5pt; color: #20445d; margin: 6mm 0 2mm;
     break-after: avoid; overflow-wrap: anywhere; }
h4 { font-size: 10pt; color: #20445d; margin: 5mm 0 2mm;
     break-after: avoid; }
p { margin: 0 0 3mm; }
ul, ol { margin-top: 0; padding-left: 6mm; }
li { margin-bottom: 1.5mm; }
blockquote { margin: 3mm 0; border-left: 3px solid #9cafc0; padding: 2mm 3mm;
             background: #f5f8fa; }
table { border-collapse: collapse; width: 100%; table-layout: auto;
        font-size: 8.3pt; line-height: 1.24; margin: 3mm 0 5mm; }
th, td { border: 1px solid #d2dce5; padding: 1.8mm 2mm;
         text-align: left; vertical-align: top; overflow-wrap: anywhere;
         word-wrap: break-word; word-break: break-word; hyphens: auto; }
th { color: #153a5a; background-color: #eaf1f7; font-weight: 700; }
tbody tr:nth-child(even) { background-color: #f8fafc; }
thead { display: table-header-group; }
tr { break-inside: avoid; }
code { font-family: Consolas, 'DejaVu Sans Mono', monospace;
       font-size: .88em; white-space: pre-wrap; overflow-wrap: anywhere;
       word-break: break-word; }
pre { background: #f5f8fa; padding: 3mm;
      border: 1px solid #d2dce5; white-space: pre-wrap;
      overflow-wrap: anywhere; font-size: 9pt; break-inside: avoid; }
pre code { white-space: pre-wrap; }
a { color: #185a88; text-decoration: none; overflow-wrap: anywhere; }
@media print { a { color: #20445d; } }
"""


def run(args: list[str], *, label: str) -> None:
    try:
        subprocess.run(args, check=True, stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, text=True)
    except subprocess.CalledProcessError as exc:
        sys.stderr.write(f'{label} failed (exit code {exc.returncode}).\n')
        sys.stderr.write((exc.stderr or exc.stdout or '')[-4000:] + '\n')
        raise SystemExit(1) from exc


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('markdown', type=Path, help='Input Markdown file')
    parser.add_argument('-o', '--output', type=Path,
                        help='Output PDF; default: exports/<input stem>.pdf')
    parser.add_argument('--portrait', action='store_true',
                        help='Use portrait A4 instead of landscape A4')
    parser.add_argument('--refresh', action='store_true',
                        help='First run scripts/reporting/build_data_summary.py')
    ns = parser.parse_args()

    if ns.refresh:
        generator = Path('scripts/reporting/build_data_summary.py')
        if not generator.exists():
            parser.error('--refresh must run from the repository root')
        run([sys.executable, str(generator)], label='Summary regeneration')

    source = ns.markdown.expanduser().resolve()
    if not source.is_file():
        parser.error(f'Input Markdown file not found: {source}')
    pandoc = shutil.which('pandoc')
    if not pandoc:
        parser.error('Pandoc is required: https://pandoc.org/installing.html')
    try:
        from weasyprint import HTML
    except ImportError:
        parser.error('WeasyPrint is required: python -m pip install weasyprint')

    out = (ns.output or Path('exports') / (source.stem + '.pdf')).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix='mdpdf_') as work:
        work = Path(work)
        css = work / 'print.css'
        css.write_text(CSS.replace('A4 landscape', 'A4 portrait') if ns.portrait else CSS,
                       encoding='utf-8')
        html = work / 'document.html'
        run([pandoc, str(source), '--from=gfm', '--to=html5', '--standalone',
             '--metadata', f'title={source.stem.replace("_", " ")}',
             '--resource-path', str(source.parent),
             '--css', css.as_uri(), '-o', str(html)], label='Markdown -> HTML')
        HTML(filename=str(html), base_url=str(source.parent)).write_pdf(str(out))
    if not out.exists() or out.stat().st_size < 1000:
        parser.error(f'The browser did not create a valid PDF: {out}')
    print(f'PDF created: {out}')


if __name__ == '__main__':
    main()
