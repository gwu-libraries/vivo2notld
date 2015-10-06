from flask import Flask, render_template, request, session, Response
import argparse
from vivo2notld.definitions import definitions, list_definitions
from vivo2notld.utility import execute, execute_list

formats = {
    "xml": "text/xml",
    "json": "text/json",
    "yaml": "text/yaml"
}

app = Flask(__name__)
default_definition = None
default_list_definition = None
default_subject_namespace = None
default_subject_identifier = None
default_list_subject_namespace = None
default_list_subject_identifier = None
default_endpoint = None
default_username = None
default_password = None
default_format = None
default_definition_type = "list"
default_list_limit = 10
default_is_limited = False
default_list_offset = None
default_is_offset = False


def get_definitions(defs):
    return {definition: definition.replace("_", " ") for definition in defs}


@app.route('/', methods=["GET"])
def crosswalk_form(output=None, obj=None, graph=None, query=None, select_query=None, count_query=None):
    return render_template("crosswalk_form.html",
                           definition_type=session.get("definition_type") or default_definition_type,
                           definitions=get_definitions(definitions),
                           list_definitions=get_definitions(list_definitions),
                           definition=session.get("definition") or default_definition,
                           list_definition=session.get("list_definition") or default_list_definition,
                           subject_namespace=session.get("subject_namespace") or default_subject_namespace,
                           subject_identifier=session.get("subject_identifier") or default_subject_identifier,
                           list_subject_namespace=session.get("list_subject_namespace")
                                                  or default_list_subject_namespace,
                           list_subject_identifier=session.get("list_subject_identifier")
                                                  or default_list_subject_identifier,
                           list_limit=session.get("list_limit") or default_list_limit,
                           is_limited=session.get("is_limited") or default_is_limited,
                           list_offset=session.get("list_offset") or default_list_offset,
                           is_offset=session.get("is_offset") or default_is_offset,
                           endpoint=session.get("endpoint") or default_endpoint,
                           username=session.get("username") or default_username,
                           password=session.get("password") or default_password,
                           format=session.get("format") or default_format,
                           output_html=session.get("output_html", True),
                           output=output,
                           obj=obj,
                           graph=graph.serialize(format="turtle").decode("utf-8") if graph else None,
                           query=query,
                           select_query=select_query,
                           count_query=count_query)


@app.route('/', methods=["POST"])
def crosswalk():
    session["definition"] = request.form.get("definition")
    session["list_definition"] = request.form.get("list_definition")
    session["subject_namespace"] = request.form.get("subject_namespace")
    session["subject_identifier"] = request.form.get("subject_identifier")
    session["list_subject_namespace"] = request.form.get("list_subject_namespace")
    session["list_subject_identifier"] = request.form.get("list_subject_identifier")
    session["list_limit"] = request.form.get("list_limit")
    session["is_limited"] = True if "is_limited" in request.form else False
    session["list_offset"] = request.form.get("list_offset")
    session["is_offset"] = True if "is_offset" in request.form else False
    session["endpoint"] = request.form.get("endpoint")
    session["username"] = request.form.get("username")
    session["password"] = request.form.get("password")
    session["format"] = request.form.get("format")
    session["output_html"] = True if "output_html" in request.form else False
    session["definition_type"] = request.form.get("definition_type")

    select_q = None
    count_q = None

    definition_type = request.form.get("definition_type")
    if not definition_type:
        if "definition" in request.form and "list_definition" not in request.form:
            definition_type = "individual"
        elif "definition" not in request.form and "list_definition" in request.form:
            definition_type = "list"
        else:
            definition_type = default_definition_type

    if definition_type == "individual":
        o, s, g, q = execute(definitions[request.form.get("definition", default_definition)],
                             request.form.get("subject_namespace", default_subject_namespace),
                             request.form.get("subject_identifier", default_subject_identifier),
                             request.form.get("endpoint", default_endpoint),
                             request.form.get("username", default_username),
                             request.form.get("password", default_password),
                             serialization_format=request.form.get("format", default_format))
    else:
        o, s, g, q, select_q, count_q = execute_list(
            list_definitions[request.form.get("list_definition", default_list_definition)],
            request.form.get("list_subject_namespace", default_subject_namespace),
            request.form.get("list_subject_identifier", default_subject_identifier),
            request.form.get("endpoint", default_endpoint),
            request.form.get("username", default_username),
            request.form.get("password", default_password),
            serialization_format=request.form.get("format", default_format),
            offset=request.form.get("list_offset", default_list_offset) if "is_offset" in request.form else None,
            limit=request.form.get("list_limit", default_list_limit) if "is_limited" in request.form else None,
        )

    if "output_html" in request.form:
        return crosswalk_form(output=o, obj=s, graph=g, query=q, select_query=select_q,
                              count_query=count_q)
    else:
        return Response(o, content_type=formats[request.form.get("format", default_format)])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--port", type=int, default="5000", help="The port the service should run on. Default is 5000.")

    parser.add_argument("--format", default="json", choices=formats.keys(),
                        help="The format for serializing. Default is json.")
    parser.add_argument("--endpoint", dest="endpoint",
                        help="Endpoint for SPARQL Query of VIVO instance,e.g., http://localhost/vivo/api/sparqlQuery.")
    parser.add_argument("--username", dest="username", help="Username for VIVO root.")
    parser.add_argument("--password", dest="password",
                        help="Password for VIVO root.")
    parser.add_argument("--namespace", default="http://vivo.mydomain.edu/individual/",
                        help="Namespace for the subject. Default is http://vivo.mydomain.edu/individual/.")
    parser.add_argument("--identifier", help="Identifier for the subject, e.g., n123.")
    parser.add_argument("--list-namespace", default="http://vivo.mydomain.edu/individual/",
                        help="Namespace for the list subject. Default is http://vivo.mydomain.edu/individual/.")
    parser.add_argument("--list-identifier", help="Identifier for the list subject, e.g., n123.")
    parser.add_argument("--definition", default="person", choices=definitions.keys(),
                        help="Default is person.")
    parser.add_argument("--list-definition", default="person_summary_with_positions_in",
                        choices=list_definitions.keys(),
                        help="Default is person_summary_with_positions_in.")
    parser.add_argument("--limit", type=int, help="List limit.")
    parser.add_argument("--offset", type=int, help="List offset.")

    #Parse
    args = parser.parse_args()

    app.debug = args.debug
    app.secret_key = "vivo2notld"

    default_definition = args.definition
    default_list_definition = args.list_definition
    default_subject_namespace = args.namespace
    default_subject_identifier = args.identifier
    default_list_subject_namespace = args.list_namespace
    default_list_subject_identifier = args.list_identifier
    default_endpoint = args.endpoint
    default_username = args.username
    default_password = args.password
    default_format = args.format
    if args.limit:
        default_list_limit = args.limit
        default_is_limited = True
    if args.offset:
        default_list_offset = args.offset
        default_is_offset = True

    app.run(host="0.0.0.0", port=args.port)