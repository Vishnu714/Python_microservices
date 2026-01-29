
from typing import Any, Dict, List
import json
import sys
from nlp_service import NLPService

svc = NLPService()


def extract_entities_from_pdf_path(path: str) -> List[Dict[str, Any]]:
	return svc.process_pdf_path(path)["entities"]


def extract_entities_from_text(text: str) -> List[Dict[str, Any]]:
	return svc.process_text(text)["entities"]


if __name__ == "__main__":
	if len(sys.argv) < 2:
		print("Usage: python entitiy_extraction.py <file.pdf>")
		sys.exit(1)
	out = svc.process_pdf_path(sys.argv[1])
	print(json.dumps(out, indent=2))

