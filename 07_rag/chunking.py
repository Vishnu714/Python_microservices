from PyPDF2 import PdfReader
import uuid

def load_pdf_text(path):
    reader=PdfReader(path)
    pages=[]
    for i,page in enumerate(reader.pages):
        text=page.extract_text() or ""
        pages.append({"page":i+1,"text":text})
    return pages

def chunk_texts(pages,chunk_size=1000,overlap=200):
    chunks=[]
    for p in pages:
        text=p["text"].strip()
        if not text:
            continue
        start=0
        while start < len(text):
            end=start+chunk_size
            chunk=text[start:end]
            chunks.append({"id":str(uuid.uuid4()),"page":p["page"],"text":chunk})
            start=end-overlap
            if start<0:
                start=0
    return chunks
