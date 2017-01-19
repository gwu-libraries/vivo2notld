definition = {
    "where": "?subj a foaf:Person .",
    "fields": {
        "name": {
            "where": "?subj rdfs:label ?obj ."
        },
        "display_name": {
            "where": "?subj local:normalOrderName ?obj ."
        },
        "given_name":    {
            "where": """
                        ?subj obo:ARG_2000028 ?cvc .
                        ?cvc vcard:hasName ?nvc .
                        ?nvc vcard:givenName ?obj .
                     """,
        },
        "family_name":    {
            "where": """
                        ?subj obo:ARG_2000028 ?cvc .
                        ?cvc vcard:hasName ?nvc .
                        ?nvc vcard:familyName ?obj .
                     """,
        },
        "street_address": {
            "where": """
                ?subj obo:ARG_2000028 ?cvc .
                ?cvc vcard:hasAddress ?avc .
                ?avc vcard:streetAddress ?obj .
             """,
            "optional": True
        },
        "locality": {
            "where": """
                ?subj obo:ARG_2000028 ?cvc .
                ?cvc vcard:hasAddress ?avc .
                ?avc vcard:locality ?obj .
             """,
            "optional": True
        },
        "postal_code": {
            "where": """
                ?subj obo:ARG_2000028 ?cvc .
                ?cvc vcard:hasAddress ?avc .
                ?avc vcard:postalCode ?obj .
             """,
            "optional": True
        },
        "region": {
            "where": """
                ?subj obo:ARG_2000028 ?cvc .
                ?cvc vcard:hasAddress ?avc .
                ?avc vcard:region ?obj .
             """,
            "optional": True
        },
        "email": {
            "where": """
                ?subj obo:ARG_2000028 ?cvc .
                ?cvc vcard:hasEmail ?evc .
                ?evc vcard:email ?obj .
             """,
            "optional": True
        },
        "phone": {
            "where": """
                ?subj obo:ARG_2000028 ?cvc .
                ?cvc vcard:hasTelephone ?tvc .
                ?tvc vcard:telephone ?obj .
            """,
            "optional": True
        },
        "home_department": {
            "where": """
                ?subj local:homeDept ?org .
                ?org rdfs:label ?obj .
            """,
        },
    }
}
