from typing import Dict

from ...code_notes_exporter_base import CodeNotesExporterBase

from .code_review_exporter import CodeReviewNotesExporter

def get_exporters() -> Dict[str, CodeNotesExporterBase]:
    code_review = CodeReviewNotesExporter()
    result = {
        code_review.Name: code_review
    }
    return result