from .document_summary import definition as document_summary_definition
from .organization_summary import definition as organization_summary_definition
from .person_definition import definition as person_summary_definition

definitions = {
    "document_summary": document_summary_definition,
    "organization_summary": organization_summary_definition,
    "person": person_summary_definition
}