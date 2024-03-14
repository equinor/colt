from rdflib import Graph, RDF, OWL


class Ontology:
    graph: Graph = None
    base: str = None
    members: set = None

    def __init__(self, file_path: str):
        g = Graph()
        g.parse(file_path)
        self.graph = g

        import re

        content = open(file_path, "r").read()
        match = re.search(r"@base <(.*)>", content)

        if match:
            self.base = match.group(1)
        else:
            self.base = self.find_base()

        self.members = self.find_members()

    def find_base(self) -> str:
        if self.graph.base != None:
            return self.graph.base
        return str(self.graph.value(predicate=RDF.type, object=OWL.Ontology))

    def find_members(self) -> set:
        return {
            item for triple in self.graph for item in triple if self.is_member(item)
        }

    def version_iri(self) -> str:
        subjects = list(self.graph.subjects(predicate=OWL.versionInfo))
        if len(subjects) < 1:
            return None
        return subjects[0]

    def ontology_iri(self) -> str:
        subjects = list(self.graph.subjects(predicate=f"{OWL}ontologyIRI"))
        if len(subjects) < 1:
            return None
        return subjects[0]

    def is_member(self, iri: str) -> bool:
        return self.base != iri and self.base in iri

    def __str__(self):
        return f"{self.base}--{self.graph.identifier}"


if __name__ == "__main__":
    print("This module is only meant to be imported.")
