from .document_summary import definition as document_summary_definition
from .organization_summary import definition as organization_summary_definition
from .person_definition import definition as person_definition
from .person_summary_definition import definition as person_summary_definition
from .person_summary_with_positions_in import definition as person_summary_with_positions_in_definition

definitions = {
    "document_summary": document_summary_definition,
    "organization_summary": organization_summary_definition,
    "person": person_definition,
    "person_summary": person_summary_definition
}

list_definitions = {
    "person_summary_with_positions_in": person_summary_with_positions_in_definition
}