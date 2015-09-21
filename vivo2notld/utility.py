from vivo2notld.definitions import definitions
from vivo2notld.sparql_query import generate_sparql_construct
from vivo2notld.sparql_endpoint import query as query_endpoint
from vivo2notld.graph import transform as transform_graph
from vivo2notld.serializers import to_json, to_xml, to_yaml


def execute(definition, subject_namespace, subject_identifier, endpoint, username, password,
            serialization_format="json", indent=4):
    q = generate_sparql_construct(definition, subject_namespace, subject_identifier)
    g = query_endpoint(endpoint, username, password, q)
    s = transform_graph(g, subject_namespace + subject_identifier)
    if serialization_format == "xml":
        o = to_xml(s, indent=indent)
    elif serialization_format == "yaml":
        o = to_yaml(s, indent=indent)
    else:
        o = to_json(s, indent=indent)
    return o, s, g, q
