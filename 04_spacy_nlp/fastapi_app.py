from fastapi import FastAPI, UploadFile, File, Query
from typing import Optional
import os
import json
from nlp_service import NLPService

app = FastAPI()
svc = NLPService()


@app.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...), save: bool = Query(False), filename: Optional[str] = Query(None)
):
    data = await file.read()
    res = svc.process_pdf_bytes(data)
    if save:
        fname = filename or (file.filename + ".json")
        path = os.path.abspath(fname)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        return {"saved": path, "result": res}
    return res
