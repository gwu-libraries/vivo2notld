from unittest import TestCase
from vivo2notld.sparql_query import _format_query, generate_sparql_construct


class TestSparqlQuery(TestCase):
    def test_where(self):
        definition = {
            "where": "?subj a foaf:Person ."
        }
        q = generate_sparql_construct(definition, "http://test/", "123")
        self.assertTrue("""WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 a foaf:Person .
        ?v0 vitro:mostSpecificType ?v1 .
    }
}""" in q)

    def test_field(self):
        definition = {
            "fields": {
                "name": {
                    "where": "?subj rdfs:label ?obj ."
                }
            }
        }
        q = generate_sparql_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :type ?v1 .
    ?v0 :name ?v2 .
}
WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 vitro:mostSpecificType ?v1 .
        ?v0 rdfs:label ?v2 .
    }
}""" in q)

    def test_optional_field(self):
        definition = {
            "fields": {
                "geographicFocus": {
                    "where": "?subj vivo:geoGraphicFocus ?obj .",
                    "optional": True
                }
            }
        }
        q = generate_sparql_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :type ?v1 .
    ?v0 :geographicFocus ?v2 .
}
WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 vitro:mostSpecificType ?v1 .
    }
    OPTIONAL
    {
        ?v0 vivo:geoGraphicFocus ?v2 .
    }
}""" in q)

    def test_list_field(self):
        definition = {
            "fields": {
                "geographicFocus": {
                    "where": "?subj vivo:geoGraphicFocus ?obj .",
                    "list": True
                }
            }
        }
        q = generate_sparql_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :type ?v1 .
    ?v0 :geographicFocus ?v2 .
    ?v0 :geographicFocus rdf:List .
}""" in q)

    def test_child_field(self):
        child_definition = {
            "where": "?subj a bibo:Document .",
            "fields": {
                "title": {
                    "where": "?subj rdfs:label ?obj ."
                },
                "issue": {
                    "where": "?subj bibo:issue ?obj .",
                    "optional": True
                }
            }
        }

        definition = {
            "fields": {
                "publications": {
                    "where": """
                                ?subj vivo:relatedBy ?aship .
                                ?aship a vivo:Authorship .
                                ?aship vivo:relates ?obj .
                             """,
                    "definition": child_definition,
                    "optional": True
                }
            }
        }

        q = generate_sparql_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :type ?v1 .
    ?v0 :publications ?v2 .
    ?v2 :type ?v3 .
    ?v2 :issue ?v4 .
    ?v2 :title ?v5 .
}
WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 vitro:mostSpecificType ?v1 .
    }
    OPTIONAL
    {
        ?v0 vivo:relatedBy ?aship .
        ?aship a vivo:Authorship .
        ?aship vivo:relates ?v2 .
        ?v2 vitro:mostSpecificType ?v3 .
        ?v2 a bibo:Document .
        ?v2 rdfs:label ?v5 .
        OPTIONAL
        {
            ?v2 bibo:issue ?v4 .
        }
    }
}""" in q)

    def test_recursive_child_field(self):
        child_child_definition = {
            "where": "?subj a bibo:Journal .",
            "fields": {
                "title": {
                    "where": "?subj rdfs:label ?obj ."
                }
            }
        }
        child_definition = {
            "where": "?subj a bibo:Document .",
            "fields": {
                "journal": {
                    "where": "?subj vivo:hasPublicationVenue ?obj .",
                    "definition": child_child_definition,
                    "optional": True
                }
            }
        }

        definition = {
            "fields": {
                "publications": {
                    "where": """
                                ?subj vivo:relatedBy ?aship .
                                ?aship a vivo:Authorship .
                                ?aship vivo:relates ?obj .
                             """,
                    "definition": child_definition,
                    "optional": True
                }
            }
        }

        q = generate_sparql_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :type ?v1 .
    ?v0 :publications ?v2 .
    ?v2 :type ?v3 .
    ?v2 :journal ?v4 .
    ?v4 :type ?v5 .
    ?v4 :title ?v6 .
}
WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 vitro:mostSpecificType ?v1 .
    }
    OPTIONAL
    {
        ?v0 vivo:relatedBy ?aship .
        ?aship a vivo:Authorship .
        ?aship vivo:relates ?v2 .
        ?v2 vitro:mostSpecificType ?v3 .
        ?v2 a bibo:Document .
        OPTIONAL
        {
            ?v2 vivo:hasPublicationVenue ?v4 .
            ?v4 vitro:mostSpecificType ?v5 .
            ?v4 a bibo:Journal .
            ?v4 rdfs:label ?v6 .
        }
    }
}""" in q)

    def test_format_query(self):
        query = """PREFIX swrl:  <http://www.w3.org/2003/11/swrl#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

CONSTRUCT
{
    ?v0 :researchArea ?v1 .
        ?v0 :name ?v2 .
}

WHERE
{
BIND ((subj-ns:n115)  AS ?v0 )
{
    ?v0 a foaf:Person .
    ?v0 rdfs:label ?v2 .
}
    OPTIONAL
        {
        ?v0 vivo:relatedBy ?aship .
        ?aship a vivo:Authorship .
        OPTIONAL
    {
                    ?v3 vivo:hasPublicationVenue ?v4 .
                    ?v4 a bibo:Journal .
        }
        OPTIONAL
        {

            ?v3 bibo:issue ?v6 .
        }
    }

}"""

        formatted_query = """PREFIX swrl:  <http://www.w3.org/2003/11/swrl#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>

CONSTRUCT
{
    ?v0 :researchArea ?v1 .
    ?v0 :name ?v2 .
}
WHERE
{
    BIND ((subj-ns:n115)  AS ?v0 )
    {
        ?v0 a foaf:Person .
        ?v0 rdfs:label ?v2 .
    }
    OPTIONAL
    {
        ?v0 vivo:relatedBy ?aship .
        ?aship a vivo:Authorship .
        OPTIONAL
        {
            ?v3 vivo:hasPublicationVenue ?v4 .
            ?v4 a bibo:Journal .
        }
        OPTIONAL
        {
            ?v3 bibo:issue ?v6 .
        }
    }
}"""
        self.assertEqual(formatted_query, _format_query(query, 4))