import itertools
from .namespaces import default as default_namespaces


def generate_sparql_list_construct(definition, subject_namespace, subject_identifier,
                              namespaces=default_namespaces, limit=None, offset=None, indent_size=4):
    """
    Generate a SPARQL CONSTRUCT query for a list.

    Note that concatenating the subject_namespace and subject_identifier
    produces the subject's URI.

    The definition must contain a list_definition field.

    :param definition: definition for the construct.
    :param subject_namespace: namespace for the subject of the query.
    :param subject_identifier: identifier for the subject of the query.
    :param namespaces: map of namespace prefixes to namespaces.
    :param offset: offset into the list.
    :param limit: limit of number of entries in list.
    :param indent_size: number of spaces to use for indents in the query.
    """
    assert "list_definition" in definition

    variable_counter = itertools.count()
    subj_variable = _generate_variable_name(variable_counter)
    list_subj_variable = _generate_variable_name(variable_counter)
    type_construct, type_where = _generate_type(list_subj_variable, variable_counter)
    construct, fields_where, optionals, order_dict = _generate_fields(list_subj_variable, definition["list_definition"], variable_counter)
    query = """
{namespaces}


CONSTRUCT
{{
?{subj_variable} :result ?{list_subj_variable} .
{type_construct}
{construct}
}}
WHERE
{{
    {{
        SELECT DISTINCT {list_variables}
        WHERE
        {{
            BIND ((subj-ns:{subj_identifier})  AS ?{subj_variable} )
            {{
                {where}
                {list_subj_where}
                {type_where}
                {fields_where}
            }}
            {optionals}
        }}
        {order}
        {limit}
        {offset}
    }}
}}
        """.format(namespaces=_generate_namespaces(namespaces, subject_namespace),
                   type_construct=type_construct,
                   construct=construct,
                   list_variables=" ".join(["?v{}".format(i) for i in range(variable_counter.next())]),
                   subj_identifier=subject_identifier,
                   list_subj_variable=list_subj_variable,
                   subj_variable=subj_variable,
                   where=_generate_where(subj_variable, definition, obj_variable=list_subj_variable),
                   list_subj_where=_generate_where(list_subj_variable, definition["list_definition"]),
                   type_where=type_where,
                   fields_where=fields_where,
                   optionals=optionals,
                   order=_format_order(order_dict),
                   #For unknown reason, need to request limit + 1 on construct
                   limit="LIMIT {}".format(int(limit)+1) if limit else "",
                   offset="OFFSET {}".format(offset) if offset else "")

    select_query = """
{namespaces}


SELECT DISTINCT ?{list_subj_variable}
WHERE
{{
    BIND ((subj-ns:{subj_identifier})  AS ?{subj_variable} )
    {{
        {where}
        {list_subj_where}
        {type_where}
        {fields_where}
    }}
    {optionals}
}}
{order}
{limit}
{offset}
        """.format(namespaces=_generate_namespaces(namespaces, subject_namespace),
                   subj_identifier=subject_identifier,
                   list_subj_variable=list_subj_variable,
                   subj_variable=subj_variable,
                   where=_generate_where(subj_variable, definition, obj_variable=list_subj_variable),
                   list_subj_where=_generate_where(list_subj_variable, definition["list_definition"]),
                   type_where=type_where,
                   fields_where=fields_where,
                   optionals=optionals,
                   order=_format_order(order_dict),
                   limit="LIMIT {}".format(limit) if limit else "",
                   offset="OFFSET {}".format(offset) if offset else "")

    count_query = """
{namespaces}


SELECT (COUNT(DISTINCT ?{list_subj_variable}) as ?count)
WHERE
{{
    BIND ((subj-ns:{subj_identifier})  AS ?{subj_variable} )
    {{
        {where}
        {list_subj_where}
        {type_where}
        {fields_where}
    }}
    {optionals}
}}""".format(namespaces=_generate_namespaces(namespaces, subject_namespace),
             subj_identifier=subject_identifier,
             list_subj_variable=list_subj_variable,
             subj_variable=subj_variable,
             where=_generate_where(subj_variable, definition, obj_variable=list_subj_variable),
             list_subj_where=_generate_where(list_subj_variable, definition["list_definition"]),
             type_where=type_where,
             fields_where=fields_where,
             optionals=optionals)

    return _format_query(query, indent_size), \
           _format_query(select_query, indent_size), \
           _format_query(count_query, indent_size)


def generate_sparql_construct(definition, subject_namespace, subject_identifier,
                              namespaces=default_namespaces, indent_size=4):
    """
    Generate a SPARQL CONSTRUCT query for a subject.

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
    construct, fields_where, optionals, _ = _generate_fields(subj_variable_name, definition, variable_counter)
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


def _generate_where(subj_variable, definition, obj_variable=None):
    if "where" in definition:
        return _format_where(definition["where"], subj_variable, obj_variable=obj_variable)
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

    :return:  CONSTRUCT SPARQL, WHERE SPARQL, OPTIONAL SPARQL, order dict {position:(variable, is ascending)}
    """
    constructs = []
    wheres = []
    optionals = []
    extra_optionals = []
    order_dict = {}

    if "fields" in definition:
        for field in definition["fields"]:
            field_variable_name = _generate_variable_name(variable_counter)
            #Constructs
            constructs.append("?{subj} :{field} ?{obj} .".format(subj=subj_variable_name, field=field,
                                                                 obj=field_variable_name))
            #Order
            if "order" in definition["fields"][field]:
                assert isinstance(definition["fields"][field]["order"], int)
                order_dict[definition["fields"][field]["order"]] = (field_variable_name, definition["fields"][field].get("order_asc", True))

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
                child_construct, child_where, child_optional, child_order_dict = \
                    _generate_fields(field_variable_name, definition["fields"][field]["definition"], variable_counter)
                constructs.append(child_construct)
                order_dict.update(child_order_dict)
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
        return "\n".join(constructs), "\n".join(wheres), _format_optionals(optionals, extra_optionals), order_dict
    else:
        return "", "", "", {}


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
    found_start = False
    for line in split_query:
        strip_line = line.strip()
        #Remove blank lines
        if strip_line == "" and found_start:
            continue
        if "CONSTRUCT" in strip_line or "SELECT" in strip_line:
            found_start = True
        if strip_line == "}":
            indent_level -= 1
        new_split_query.append("{indent}{line}".format(indent=" " * indent_size * indent_level, line=strip_line))
        if strip_line == "{":
            indent_level += 1
    return "\n".join(new_split_query)


def _format_order(order_dict):
    """
    Formats an order dict into an ORDER BY clause.
    """
    if order_dict:
        return "ORDER BY " + " ".join(["{}(?{})".format("ASC" if order_dict[pos][1] else "DESC", order_dict[pos][0]) for pos in sorted(order_dict)])
    return ""
