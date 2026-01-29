from entity_relation import extract_entities_relations
from graph_builder import InMemoryGraph
import json

resume_json_path=r"C:\Users\vishn\py_microservices\04_spacy_nlp\Vishnu_Resume_2026.json"
with open(resume_json_path) as f:
    resume_data=json.load(f)

text=resume_data["text"]
entities=resume_data["entities"]

result=extract_entities_relations(text)
graph=InMemoryGraph()
graph.add_triples(result["triples"])

print("SPACY EXTRACTED ENTITIES FROM RESUME")
print()
entity_types={}
for ent in entities[:30]:
    label=ent["label"]
    if label not in entity_types:
        entity_types[label]=[]
    entity_types[label].append(ent["text"][:50])

for label,ents in sorted(entity_types.items()):
    print(f"{label}: {', '.join(ents[:5])}")
print()

print("EXTRACTED RELATIONSHIPS (TRIPLES)")
for t in result["triples"][:10]:
    print(f"  {t[0]} --{t[1]}--> {t[2]}")
print()

print("GRAPH QUERIES")
neighbors=graph.get_node_neighbors("Vishnu")
if neighbors["outgoing"] or neighbors["incoming"]:
    print("Relations involving 'Vishnu':")
    for e in neighbors["outgoing"][:3]:
        print(f"  {e}")
print()
