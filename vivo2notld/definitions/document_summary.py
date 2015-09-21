from .organization_summary import definition as organization_summary_definition

definition = {
    "where": "?subj a bibo:Document .",
    "fields": {
        "title": {
            "where": "?subj rdfs:label ?obj ."
        },
        "issue": {
            "where": "?subj bibo:issue ?obj .",
            "optional": True
        },
        "volume": {
            "where": "?subj bibo:volume ?obj .",
            "optional": True
        },
        "publishedIn": {
            "where": "?subj vivo:hasPublicationVenue ?obj .",
            "definition": {
                "fields": {
                    "title": {
                        "where": "?subj rdfs:label ?obj ."
                    }
                }
            },
            "optional": True
        },
        "publisher": {
            "where": "?subj vivo:publisher ?obj .",
            "definition": organization_summary_definition,
            "optional": True
        },
        "publicationDate": {
            "where": """
                        ?subj vivo:dateTimeValue ?dtv .
                        ?dtv vivo:dateTime ?obj .
                     """,
            "optional": True
        },
        "doi": {
            "where": "?subj bibo:doi ?obj .",
            "optional": True
        }
    }
}
