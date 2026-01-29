from typing import Any, Dict, List
import io
import spacy
from PyPDF2 import PdfReader


class NLPService:
    def __init__(self, model_name: str = "en_core_web_sm"):
        self.nlp = spacy.load(model_name)

    def process_text(self, text: str) -> Dict[str, Any]:
        doc = self.nlp(text)
        tokens = [
            {"text": token.text, "lemma": token.lemma_, "pos": token.pos_, "tag": token.tag_}
            for token in doc
        ]
        entities = [
            {"text": ent.text, "label": ent.label_, "start_char": ent.start_char, "end_char": ent.end_char}
            for ent in doc.ents
        ]
        return {"text": text, "tokens": tokens, "entities": entities}

    def process_pdf_bytes(self, file_bytes: bytes) -> Dict[str, Any]:
        reader = PdfReader(io.BytesIO(file_bytes))
        pages: List[str] = []
        for p in reader.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        text = "\n".join(pages)
        return self.process_text(text)

    def process_pdf_path(self, path: str) -> Dict[str, Any]:
        with open(path, "rb") as f:
            return self.process_pdf_bytes(f.read())
