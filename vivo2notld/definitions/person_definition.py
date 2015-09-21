from .document_summary import definition as document_summary_definition
from .organization_summary import definition as organization_summmary_definition

definition = {
    "where": "?subj a foaf:Person .",
    "fields": {
        "name": {
            "where": "?subj rdfs:label ?obj ."
        },
        #Contact info
        "email": {
            "where": """
                        ?subj obo:ARG_2000028 ?vc .
                        ?vc a vcard:Kind .
                        ?vc vcard:hasEmail ?vce .
                        ?vce a vcard:Email, vcard:Work .
                        ?vce vcard:email ?obj .
                     """
        },
        "telephone": {
            "where": """
                        ?subj obo:ARG_2000028 ?vc .
                        ?vc a vcard:Kind .
                        ?vc vcard:hasTelephone ?vct .
                        ?vct a vcard:Telephone .
                        ?vct vcard:telephone ?obj .
                     """
        },
        "address": {
            "where": """
                        ?subj obo:ARG_2000028 ?vc .
                        ?vc a vcard:Kind .
                        ?vc vcard:hasAddress ?obj .
                     """,
            "definition": {
                "where": "?subj a vcard:Address .",
                "fields": {
                    "address": {
                        "where": "?subj vcard:streetAddress ?obj ."
                    },
                    "city": {
                        "where": "?subj vcard:locality ?obj ."
                    },
                    "state": {
                        "where": "?subj vcard:region ?obj ."
                    },
                    "zip": {
                        "where": "?subj vcard:postalCode ?obj ."
                    }
                }
            }
        },
        "website": {
            "list": True,
            "where": """
                        ?subj obo:ARG_2000028 ?vc .
                        ?vc a vcard:Kind .
                        ?vc vcard:hasURL ?vcu .
                        ?vcu a vcard:URL .
                        ?vcu vcard:url ?obj .
                     """
        },
        "researchArea": {
            "where": """
                        ?subj vivo:hasResearchArea ?ra .
                        ?ra rdfs:label ?obj .
                     """,
            "optional": True,
            "list": True
        },
        "geographicFocus": {
            "where": """
                        ?subj vivo:geographicFocus ?gf .
                        ?gf rdfs:label ?obj .
                     """,
            "optional": True,
            "list": True
        },
        "overview": {
            "where": "?subj vivo:overview ?obj .",
            "optional": True,
        },
        "positions": {
            "where": "?subj vivo:relatedBy ?obj .",
            "definition": {
                "where": "?subj a vivo:Position .",
                "fields": {
                    "title": {
                        "where": "?subj rdfs:label ?obj ."
                    },
                    "organization": {
                        "where": "?subj vivo:relates ?obj .",
                        "definition": organization_summmary_definition
                    }
                }
            },
            "optional": True,
            "list": True
        },
        "publications": {
            "where": """
                        ?subj vivo:relatedBy ?aship .
                        ?aship a vivo:Authorship .
                        ?aship vivo:relates ?obj .
                     """,
            "definition": document_summary_definition,
            "optional": True,
            "list": True
        }
    }
}
