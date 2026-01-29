
import re
from typing import Optional


def clean_text(text: str, remove_newlines: Optional[bool] = True) -> str:
	if not text:
		return ""
	s = text.replace("\r", "\n")
	if remove_newlines:
		s = " ".join(s.split())
	s = re.sub(r"\s+", " ", s).strip()
	return s


if __name__ == "__main__":
	import sys
	if len(sys.argv) > 1:
		print(clean_text(sys.argv[1]))

