import sys
import json
import os
from nlp_service import NLPService


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python run_nlp.py <file.pdf> [output.json]")
        sys.exit(1)
    path = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else None
    svc = NLPService()
    out = svc.process_pdf_path(path)
    j = json.dumps(out, indent=2, ensure_ascii=False)
    if out_path:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(j)
        print(f"Saved JSON to {out_path}")
    else:
        base = os.path.splitext(os.path.basename(path))[0]
        default = base + ".json"
        with open(default, "w", encoding="utf-8") as f:
            f.write(j)
        print(f"Saved JSON to {default}")
    print(j)


if __name__ == "__main__":
    main()
