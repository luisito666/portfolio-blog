"""Render the CV PDF from the template context.

Extracted from ``apps.portfolio.views.GeneratePDFView`` so the PDF
generation pipeline can be reused by the AI-adapted CV flow.
"""

import io

from django.template.loader import get_template
from weasyprint import HTML

TEMPLATE_NAME = 'portfolio/cv_pdf.html'


def generate_cv_pdf(context, output_path=None):
    """Render ``portfolio/cv_pdf.html`` with ``context`` into a PDF.

    If ``output_path`` is provided the PDF bytes are written to that file
    and the path is returned. When ``output_path`` is ``None`` the PDF
    bytes are returned directly.
    """
    template = get_template(TEMPLATE_NAME)
    html = template.render(context)

    if output_path:
        HTML(string=html).write_pdf(output_path)
        return output_path

    buffer = io.BytesIO()
    HTML(string=html).write_pdf(buffer)
    return buffer.getvalue()