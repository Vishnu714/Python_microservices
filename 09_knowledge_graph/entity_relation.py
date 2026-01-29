import spacy
from typing import List, Tuple

nlp=spacy.load("en_core_web_sm")

def extract_entities(text):
    doc=nlp(text)
    entities=[(ent.text,ent.label_) for ent in doc.ents]
    return entities

def extract_relations(text):
    doc=nlp(text)
    triples=[]
    for token in doc:
        if token.dep_ in ("nsubj","nsubjpass"):
            subj=token.text
            verb=token.head.text
            for child in token.head.children:
                if child.dep_ in ("dobj","attr","prep"):
                    obj=child.text
                    triples.append((subj,verb,obj))
    return triples

def extract_entities_relations(text):
    entities=extract_entities(text)
    triples=extract_relations(text)
    return {"entities":entities,"triples":triples}
