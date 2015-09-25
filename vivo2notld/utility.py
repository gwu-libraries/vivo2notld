from vivo2notld.sparql_query import generate_sparql_construct, generate_sparql_list_construct
from vivo2notld.sparql_endpoint import query, select_query
from vivo2notld.graph import transform as transform_graph
from vivo2notld.serializers import to_json, to_xml, to_yaml


def execute(definition, subject_namespace, subject_identifier, endpoint, username, password,
            serialization_format="json", indent_size=4):
    q = generate_sparql_construct(definition, subject_namespace, subject_identifier, indent_size=indent_size)
    g = query(endpoint, username, password, q)
    s = transform_graph(g, subject_namespace + subject_identifier)
    o = _serialize(s, serialization_format, indent_size)
    return o, s, g, q


def execute_list(definition, subject_namespace, subject_identifier, endpoint, username, password,
                 serialization_format="json", indent_size=4, offset=None, limit=None):
    q, select_q, count_q = generate_sparql_list_construct(definition, subject_namespace, subject_identifier,
                                                          indent_size=indent_size, offset=offset, limit=limit)
    g = query(endpoint, username, password, q)
    select_results = select_query(endpoint, username, password, select_q)
    result_list = []
    for result in select_results["results"]["bindings"]:
        result_list.append(transform_graph(g, result["v1"]["value"]))
    count_results = select_query(endpoint, username, password, count_q)
    result = {
        "list": result_list,
        "count": int(count_results["results"]["bindings"][0]["count"]["value"])
    }
    if offset:
        result["offset"] = offset
    if limit:
        result["limit"] = limit

    o = _serialize(result, serialization_format, indent_size)
    return o, result, g, q, select_q, count_q


def _serialize(obj, serialization_format, indent):
    if serialization_format == "xml":
        return to_xml(obj, indent=indent)
    elif serialization_format == "yaml":
        return to_yaml(obj, indent=indent)
    else:
        return to_json(obj, indent=indent)

