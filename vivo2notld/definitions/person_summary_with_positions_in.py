from .person_summary_definition import definition as person_summary_definition

mod_person_summary_definition = person_summary_definition.copy()
mod_person_summary_definition["fields"]["name"]["order"] = 1

definition = {
    "where": """
                ?subj vivo:relatedBy ?pos .
                ?pos a vivo:Position .
                ?pos vivo:relates ?obj .
             """,
    "list_definition": mod_person_summary_definition
}
