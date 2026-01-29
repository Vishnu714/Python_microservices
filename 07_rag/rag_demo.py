from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0,str(ROOT))
from chunking import load_pdf_text,chunk_texts
from retriever import Retriever
from app.core.llm_client import call_llm
import json
from datetime import datetime

def main():
    pdf_path=r"C:\Users\vishn\Downloads\Vishnu_Resume_2026.pdf"
    pages=load_pdf_text(pdf_path)
    chunks=chunk_texts(pages,chunk_size=800,overlap=200)
    retr=Retriever()
    retr.build(chunks)
    query="Summarize the candidate's top ML skill "
    direct=call_llm("You are an assistant that answers",query,timeout=20)
    retrieved=retr.retrieve(query,k=2)
    context="\n\n".join([f'[{r["score"]:.3f}] {r["doc"]["text"][:300]}' for r in retrieved])
    prompt_with_context=f"summary of the candidate's top skill.\n\nContext:\n{context}\n\nQuestion:\n{query}"
    rag_answer=call_llm("You are an assistant that answers in para.",prompt_with_context,timeout=20)
    if not rag_answer or rag_answer.startswith("LLM_ERROR"):
        if retrieved and retrieved[0]["doc"]["text"].strip():
            first=retrieved[0]["doc"]["text"].strip()
            first_sentence=first.split(".\n")[0].split(".")[0].strip()
            rag_answer=(first_sentence+".") if first_sentence else first[:200]
        else:
            rag_answer="No summary available."
    if not direct or direct.startswith("LLM_ERROR"):
        direct=rag_answer
    print("DIRECT ANSWER")
    print(direct)
    print()
    print("RAG ANSWER")
    print(rag_answer)
    print()
    out={"query":query,"direct_answer":direct,"rag_answer":rag_answer,"pdf_path":pdf_path,"timestamp":datetime.utcnow().isoformat()+"Z","retrieved":[{"score":r["score"],"id":r["doc"].get("id"),"page":r["doc"].get("page"),"text":r["doc"]["text"][:500]} for r in retrieved]}
    out_path=Path(__file__).resolve().parent / "rag_result.json"
    out_path.write_text(json.dumps(out,ensure_ascii=False,indent=2))
    print("Saved RAG result to",out_path)

if __name__=='__main__':
    main()
