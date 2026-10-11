import csv
import uuid

from ...code_notes_exporter_base import CodeNotesExporterBase
from ...entity import NoteImportance

class CodeReviewNotesExporter(CodeNotesExporterBase):
    """Notes exporter for code review VSCode plugin (https://marketplace.visualstudio.com/items?itemName=d-koppenhagen.vscode-code-review)
    """
      
    cCsvColumns = [
        "sha", 
        "filename", 
        "url", 
        "lines", 
        "title", 
        "comment", 
        "priority", 
        "category", 
        "additional", 
        "id", 
        "private"
    ]

    cNoteImportanceToPriority = {
        NoteImportance.INFO: "0",
        NoteImportance.LOW: "1",
        NoteImportance.MEDIUM: "2",
        NoteImportance.HIGH: "3"
    }

    @property
    def Name(self):
        return "codereview"

    def export(self, path_mappings, notes, output):
        with open(output, "w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(fp, fieldnames=CodeReviewNotesExporter.cCsvColumns)

            writer.writeheader()
            for note in notes:
                mapped_path = note.file
                for mapping_from, _ in path_mappings.items():
                    if mapped_path.startswith(mapping_from):
                        mapped_path = mapped_path.replace(mapping_from, "/")
                        break
                writer.writerow({
                    "sha": "",
                    "filename": mapped_path,
                    "url":"",
                    "lines":f"{note.line}:1-{note.line}:1",
                    "title":note.note,
                    "comment":"",
                    "priority":CodeReviewNotesExporter.cNoteImportanceToPriority[note.importance],
                    "category":"",
                    "additional":note.note_type,
                    "id":str(uuid.uuid4()),
                    "private":"0"
                })

