from unittest import TestCase
from vivo2notld.sparql_query import _format_query, generate_sparql_construct, generate_sparql_list_construct


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

    def test_list_definition(self):
        definition = {
            "list_definition": {
                "where": "?subj a foaf:Person .",
                "fields": {
                    "name": {
                        "where": "?subj rdfs:label ?obj ."
                    }
                }
            }
        }
        q, _, _ = generate_sparql_list_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :result ?v1 .
    ?v1 :type ?v2 .
    ?v1 :name ?v3 .
}
WHERE
{
    {
        SELECT DISTINCT ?v0 ?v1 ?v2 ?v3
        WHERE
        {
            BIND ((subj-ns:123)  AS ?v0 )
            {
                ?v1 a foaf:Person .
                ?v1 vitro:mostSpecificType ?v2 .
                ?v1 rdfs:label ?v3 .
            }
        }
    }
}""" in q)

    def test_list_where(self):
        definition = {
            "where": """
                ?subj vivo:relatedBy ?pos .
                ?pos a vivo:Position .
                ?pos vivo:relates ?obj .
             """,
            "list_definition": {
            }
        }
        q, _, _ = generate_sparql_list_construct(definition, "http://test/", "123")
        self.assertTrue("""CONSTRUCT
{
    ?v0 :result ?v1 .
    ?v1 :type ?v2 .
}
WHERE
{
    {
        SELECT DISTINCT ?v0 ?v1 ?v2
        WHERE
        {
            BIND ((subj-ns:123)  AS ?v0 )
            {
                ?v0 vivo:relatedBy ?pos .
                ?pos a vivo:Position .
                ?pos vivo:relates ?v1 .
                ?v1 vitro:mostSpecificType ?v2 .
            }
        }
    }
}""" in q)

    def test_list_order_by(self):
        definition = {
            "list_definition": {
                "where": "?subj a foaf:Person .",
                "fields": {
                    "name": {
                        "where": "?subj rdfs:label ?obj .",
                        "order": 2,
                        "order_asc": False
                    },
                    "researchArea": {
                        "where": "?subj vivo:hasResearchArea ?obj .",
                        "order": 1
                    }
                }
            }
        }
        q, _, _ = generate_sparql_list_construct(definition, "http://test/", "123")
        self.assertTrue("ORDER BY ASC(?v3) DESC(?v4)" in q)

    def test_limit_and_offset(self):
        definition = {
            "list_definition": {
                "where": "?subj a foaf:Person .",
                "fields": {
                    "name": {
                        "where": "?subj rdfs:label ?obj ."
                    }
                }
            }
        }
        q, _, _ = generate_sparql_list_construct(definition, "http://test/", "123", limit=5, offset=10)
        self.assertTrue("""
        LIMIT 6
        OFFSET 10""" in q)

    def test_select_and_count_queries(self):
        definition = {
            "where": """
                        ?subj vivo:relatedBy ?obj .
                     """,
            "list_definition": {
                "where": "?subj a foaf:Person .",
                "fields": {
                    "name": {
                        "where": "?subj rdfs:label ?obj .",
                        "order": 1,
                    }
                }
            }
        }
        q, select_q, count_q = generate_sparql_list_construct(definition, "http://test/", "123", limit=5, offset=10)
        print select_q
        self.assertTrue("""SELECT DISTINCT ?v1
WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 vivo:relatedBy ?v1 .
        ?v1 a foaf:Person .
        ?v1 vitro:mostSpecificType ?v2 .
        ?v1 rdfs:label ?v3 .
    }
}
ORDER BY ASC(?v3)
LIMIT 5
OFFSET 10""" in select_q)

        self.assertTrue("""SELECT (COUNT(DISTINCT ?v1) as ?count)
WHERE
{
    BIND ((subj-ns:123)  AS ?v0 )
    {
        ?v0 vivo:relatedBy ?v1 .
        ?v1 a foaf:Person .
        ?v1 vitro:mostSpecificType ?v2 .
        ?v1 rdfs:label ?v3 .
    }
}""" in count_q)
