import itertools
from .namespaces import default as default_namespaces


def generate_sparql_construct(definition, subject_namespace, subject_identifier,
                              namespaces=default_namespaces, indent_size=4):
    """
    Generate a SPARQL CONSTRUCT query.

    Note that concatenating the subject_namespace and subject_identifier
    produces the subject's URI.

    :param definition: definition for the construct.
    :param subject_namespace: namespace for the subject of the query.
    :param subject_identifier: identifier for the subject of the query.
    :param namespaces: map of namespace prefixes to namespaces.
    :param indent_size: number of spaces to use for indents in the query.
    """
    variable_counter = itertools.count()
    subj_variable_name = _generate_variable_name(variable_counter)
    type_construct, type_where = _generate_type(subj_variable_name, variable_counter)
    construct, fields_where, optionals = _generate_fields(subj_variable_name, definition, variable_counter)
    query = """
{namespaces}


CONSTRUCT
{{
{type_construct}
{construct}
}}
WHERE
{{
    BIND ((subj-ns:{subject_identifier})  AS ?{subject_variable} )
    {{
        {where}
        {type_where}
        {fields_where}
    }}
    {optionals}
}}
        """.format(namespaces=_generate_namespaces(namespaces, subject_namespace),
                   type_construct=type_construct,
                   construct=construct,
                   subject_identifier=subject_identifier,
                   subject_variable=subj_variable_name,
                   where=_generate_where(subj_variable_name, definition),
                   type_where=type_where,
                   fields_where=fields_where,
                   optionals=optionals)
    return _format_query(query, indent_size)


def _generate_where(subj_variable_name, definition):
    if "where" in definition:
        return _format_where(definition["where"], subj_variable_name)
    else:
        return ""


def _generate_type(subj_variable_name, variable_counter):
    """
    Generates SPARQL for the type of a subject.

    :return:  CONSTRUCT SPARQL, WHERE SPARQL
    """
    type_variable_name = _generate_variable_name(variable_counter)
    construct = "?{subj} :type ?{obj} .".format(subj=subj_variable_name, obj=type_variable_name)
    where = "?{subj} vitro:mostSpecificType ?{obj} .".format(subj=subj_variable_name, obj=type_variable_name)
    return construct, where


def _generate_namespaces(namespaces, subject_namespace):
    """
    Generate SPARQL for namespaces.
    """
    all_namespaces = dict(namespaces)
    all_namespaces["subj-ns"] = subject_namespace
    all_namespaces[""] = "info://vivo2notld#"
    return "\n".join(["PREFIX {}:  <{}>".format(prefix, namespace) for prefix, namespace in all_namespaces.items()])


def _generate_fields(subj_variable_name, definition, variable_counter):
    """
    Generates SPARQL for the fields in a definition.

    :return:  CONSTRUCT SPARQL, WHERE SPARQL, OPTIONAL SPARQL
    """
    constructs = []
    wheres = []
    optionals = []
    extra_optionals = []
    if "fields" in definition:
        for field in definition["fields"]:
            field_variable_name = _generate_variable_name(variable_counter)
            #Constructs
            constructs.append("?{subj} :{field} ?{obj} .".format(subj=subj_variable_name, field=field,
                                                                 obj=field_variable_name))
            #If a list, add marker
            if definition["fields"][field].get("list"):
                constructs.append("?{subj} :{field} rdf:List .".format(subj=subj_variable_name, field=field))
            where = _format_where(definition["fields"][field]["where"], subj_variable_name, field_variable_name)
            if "definition" in definition["fields"][field]:
                #Type
                type_construct, type_where = _generate_type(field_variable_name, variable_counter)
                constructs.append(type_construct)
                where = "{}\n{}".format(where, type_where)

                #Recurse
                child_construct, child_where, child_optional = \
                    _generate_fields(field_variable_name, definition["fields"][field]["definition"], variable_counter)
                constructs.append(child_construct)
                where = "{}\n{}".format(where, _generate_where(field_variable_name,
                                                               definition["fields"][field]["definition"]))
                if child_where:
                    where = "{}\n{}".format(where, child_where)
                if child_optional:
                    where = "{}\n{}".format(where, child_optional)

            if not definition["fields"][field].get("optional", False):
                wheres.append(where)
            else:
                optionals.append(where)
        return "\n".join(constructs), "\n".join(wheres), _format_optionals(optionals, extra_optionals)
    else:
        return "", "", ""


def _format_where(where, subj_variable, obj_variable=None):
    """
    Format WHERE clauses, including replacing ?subj and ?obj with
    unique variable names.
    """
    new_where = where.strip()
    new_where = new_where.replace("?subj", "?{}".format(subj_variable))
    if obj_variable:
        new_where = new_where.replace("?obj", "?{}".format(obj_variable))
    return new_where


def _generate_variable_name(variable_counter):
    """
    Generates a unique variable name.
    """
    return "v{}".format(variable_counter.next())


def _format_optionals(optionals, extra_optionals):
    """
    Formats a list of optional clauses into a string containing
    multiple OPTIONALs.
    """
    optional_str = ""
    if optionals:
        for optional in optionals:
            optional_str += """OPTIONAL
            {{
                {}
            }}
            """.format(optional)
    if extra_optionals:
        optional_str += "\n".join(extra_optionals)
    return optional_str


def _format_query(query, indent_size):
    """
    Cleans up the formatting of a query including fixing indents
    and removing blank lines.
    """
    split_query = query.split("\n")
    new_split_query = []
    indent_level = 0
    found_construct = False
    for line in split_query:
        strip_line = line.strip()
        #Remove blank lines
        if strip_line == "" and found_construct:
            continue
        if "CONSTRUCT" in strip_line:
            found_construct = True
        if strip_line == "}":
            indent_level -= 1
        new_split_query.append("{indent}{line}".format(indent=" " * indent_size * indent_level, line=strip_line))
        if strip_line == "{":
            indent_level += 1
    return "\n".join(new_split_query)
