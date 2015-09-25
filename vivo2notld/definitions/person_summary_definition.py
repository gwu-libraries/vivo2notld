definition = {
    "where": "?subj a foaf:Person .",
    "fields": {
        "name": {
            "where": "?subj rdfs:label ?obj ."
        },
        "researchArea": {
            "where": """
                        ?subj vivo:hasResearchArea ?ra .
                        ?ra rdfs:label ?obj .
                     """,
            "optional": True,
            "list": True
        }
    }
}