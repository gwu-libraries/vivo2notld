from unittest import TestCase
from rdflib import Literal, URIRef, Graph, Namespace, RDF
from datetime import datetime
from vivo2notld.graph import transform


class TestGraph(TestCase):
    def setUp(self):
        self.g = Graph()
        self.n = Namespace("info://vivo2notld#")

    def test_uri(self):
        s = transform(self.g, "http://test/123")
        self.assertEqual("http://test/123", s["uri"])

    def test_single_value_field(self):
        self.g.add((URIRef("http://test/123"), self.n.name, Literal("Justin Littman")))
        s = transform(self.g, "http://test/123")
        self.assertEqual("Justin Littman", s["name"])

    def test_multiple_value_field(self):
        self.g.add((URIRef("http://test/123"), self.n.researchArea, Literal("Clouds")))
        self.g.add((URIRef("http://test/123"), self.n.researchArea, Literal("Moss")))
        s = transform(self.g, "http://test/123")
        self.assertItemsEqual(["Clouds", "Moss"], s["researchArea"])

    def test_multiple_value_marker(self):
        self.g.add((URIRef("http://test/123"), self.n.researchArea, Literal("Clouds")))
        self.g.add((URIRef("http://test/123"), self.n.researchArea, RDF.List))
        s = transform(self.g, "http://test/123")
        self.assertItemsEqual(["Clouds"], s["researchArea"])

    def test_empty_multiple_value_marker(self):
        self.g.add((URIRef("http://test/123"), self.n.researchArea, RDF.List))
        s = transform(self.g, "http://test/123")
        self.assertFalse("researchArea" in s)

    def test_child(self):
        self.g.add((URIRef("http://test/123"), self.n.publications, URIRef("http://test/456")))
        s = transform(self.g, "http://test/123")
        self.assertEqual("http://test/456", s["publications"]["uri"])

    def test_datetime(self):
        now = datetime.now()
        self.g.add((URIRef("http://test/123"), self.n.publicationDate, Literal(now)))
        s = transform(self.g, "http://test/123")
        self.assertEqual(now.isoformat(), s["publicationDate"])

