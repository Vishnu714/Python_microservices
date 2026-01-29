from typing import List, Tuple, Dict

class InMemoryGraph:
    def __init__(self):
        self.nodes=set()
        self.edges=[]
    
    def add_triple(self,subj,rel,obj):
        self.nodes.add(subj)
        self.nodes.add(obj)
        self.edges.append({"subject":subj,"relation":rel,"object":obj})
    
    def add_triples(self,triples):
        for subj,rel,obj in triples:
            self.add_triple(subj,rel,obj)
    
    def query(self,subject=None,relation=None,obj=None):
        results=[]
        for edge in self.edges:
            match=True
            if subject and edge["subject"]!=subject:
                match=False
            if relation and edge["relation"]!=relation:
                match=False
            if obj and edge["object"]!=obj:
                match=False
            if match:
                results.append(edge)
        return results
    
    def get_node_neighbors(self,node):
        outgoing=[e for e in self.edges if e["subject"]==node]
        incoming=[e for e in self.edges if e["object"]==node]
        return {"outgoing":outgoing,"incoming":incoming}

class Neo4jGraph:
    def __init__(self,uri,user,password):
        from neo4j import GraphDatabase
        self.driver=GraphDatabase.driver(uri,auth=(user,password))
    
    def add_triple(self,subj,rel,obj):
        with self.driver.session() as session:
            session.run(
                "MERGE (a:Entity {name:$s}) MERGE (b:Entity {name:$o}) MERGE (a)-[r:RELATION {type:$rel}]->(b)",
                s=subj,o=obj,rel=rel
            )
    
    def add_triples(self,triples):
        for subj,rel,obj in triples:
            self.add_triple(subj,rel,obj)
    
    def query(self,subject=None):
        with self.driver.session() as session:
            if subject:
                result=session.run(
                    "MATCH (a:Entity {name:$s})-[r]->(b) RETURN a.name,r.type,b.name",
                    s=subject
                )
            else:
                result=session.run("MATCH (a)-[r]->(b) RETURN a.name,r.type,b.name LIMIT 100")
            return [{"subject":row[0],"relation":row[1],"object":row[2]} for row in result]
    
    def close(self):
        self.driver.close()
