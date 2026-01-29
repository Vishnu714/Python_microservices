
from typing import Any, Dict, List
from nlp_service import NLPService

svc = NLPService()


def tokenize(text: str) -> List[Dict[str, Any]]:
	return svc.process_text(text)["tokens"]


def pos_tag(text: str) -> List[Dict[str, str]]:
	return [{"text": t["text"], "pos": t["pos"], "tag": t["tag"]} for t in tokenize(text)]


def extract_entities(text: str) -> List[Dict[str, Any]]:
	return svc.process_text(text)["entities"]


if __name__ == "__main__":
	import sys, json
	if len(sys.argv) < 2:
		print("Usage: python ner.py '<text>'")
	else:
		t = sys.argv[1]
		print(json.dumps(svc.process_text(t), indent=2))

