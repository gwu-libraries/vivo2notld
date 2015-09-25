# VIVO2NotLD (not Linked Data)

[![Build status](https://travis-ci.org/gwu-libraries/vivo2notld.svg)]

VIVO2NotLD provides tools to convert RDF that conforms to the VIVO-ISF Ontology
to a more simplified form encoded in JSON, XML, YAML, or other.  VIVO2NotLD can
be used to create simplified form of individuals (e.g., a person) or lists (e.g., a list of people
with positions in a specified department).

The goal of providing the simplified form is to make VIVO data more readily consumable
by other applications.  In particular, it lowers the barrier to re-use of VIVO data by:

* structuring the data in a less complex way that does not require understanding
   VIVO-ISF ontology.
* does not require understanding RDF, SPARQL, or other semantic web technologies.


Try it at http://gw-orcid2vivo.wrlc.org/vivo2notld


## Commandline

    python vivo2notld.py -h
    usage: vivo2notld.py [-h] [--format {json,yaml,xml,nt,pretty-xml,trix}]
                         [--indent INDENT] [--file FILE] [--debug]
                         [--offset OFFSET] [--limit LIMIT]
                         {person_summary,person,document_summary,organization_summary,person_summary_with_positions_in}
                         subject_namespace subject_identifier endpoint username
                         password

    positional arguments:
      {person_summary,person,document_summary,organization_summary,person_summary_with_positions_in}
      subject_namespace     For example, http://vivo.gwu.edu/individual/
      subject_identifier    For example, n115
      endpoint              Endpoint for SPARQL Query of VIVO instance,e.g.,
                            http://localhost/vivo/api/sparqlQuery.
      username              Username for VIVO root.
      password              Password for VIVO root.

    optional arguments:
      -h, --help            show this help message and exit
      --format {json,yaml,xml,nt,pretty-xml,trix}
                            The format for serializing. Default is json.
      --indent INDENT       Number of spaces to use for indents.
      --file FILE           Filepath to which to serialize.
      --debug               Also output the query, result graph, and python
                            object.
      --offset OFFSET       Offset for lists.
      --limit LIMIT         Limit for lists.

For example:

    python vivo2notld.py person http://vivo.gwu.edu/individual/ n115 http://192.168.99.100:8080/vivo/api/sparqlQuery vivo_root@gwu.edu password --debug --file=test.json

## Web application

    python vivo2notld_service.py -h
    usage: vivo2notld_service.py [-h] [--debug] [--port PORT]
                                 [--format {xml,yaml,json}] [--endpoint ENDPOINT]
                                 [--username USERNAME] [--password PASSWORD]
                                 [--namespace NAMESPACE] [--identifier IDENTIFIER]
                                 [--list-namespace LIST_NAMESPACE]
                                 [--list-identifier LIST_IDENTIFIER]
                                 [--definition {person_summary,person,document_summary,organization_summary}]
                                 [--list-definition {person_summary_with_positions_in}]
                                 [--limit LIMIT] [--offset OFFSET]

    optional arguments:
      -h, --help            show this help message and exit
      --debug
      --port PORT           The port the service should run on. Default is 5000.
      --format {xml,yaml,json}
                            The format for serializing. Default is json.
      --endpoint ENDPOINT   Endpoint for SPARQL Query of VIVO instance,e.g.,
                            http://localhost/vivo/api/sparqlUpdate.
      --username USERNAME   Username for VIVO root.
      --password PASSWORD   Password for VIVO root.
      --namespace NAMESPACE
                            Namespace for the subject. Default is
                            http://vivo.mydomain.edu/individual/.
      --identifier IDENTIFIER
                            Identifier for the subject, e.g., n123.
      --list-namespace LIST_NAMESPACE
                            Namespace for the list subject. Default is
                            http://vivo.mydomain.edu/individual/.
      --list-identifier LIST_IDENTIFIER
                            Identifier for the list subject, e.g., n123.
      --definition {person_summary,person,document_summary,organization_summary}
                            Default is person.
      --list-definition {person_summary_with_positions_in}
                            Default is person_summary_with_positions_in.
      --limit LIMIT         List limit.
      --offset OFFSET       List offset.

For example, to start:

    python vivo2notld_service.py

or:

    python vivo2notld_service.py --format json --endpoint http://192.168.99.100:8080/vivo/api/sparqlQuery --username vivo_root@gwu.edu --password password --namespace http://vivo.gwu.edu/individual/ --identifier n115 --list-namespace http://vivo.gwu.edu/individual/ --list-identifier n336 --limit 10  --debug

The web form will now be available at http://localhost:5000/.

### Invoke using curl

For an individual:

    curl --data "definition=person&subject_namespace=http://vivo.gwu.edu/individual/&subject_identifier=n115&format=json&definition_type=individual" http://localhost:5000/

For a list:

    curl --data "definition=person_summary_with_positions_in&list_subject_namespace=http://vivo.mydomain.edu/individual/&list_subject_identifier=n3360&format=json&definition_type=list&is_limited=true&limit=10&is_offset=true&offset=2" http://localhost:5000/


## Tests

    python -m unittest discover

## Transformation process

### For individuals

Note that individuals can be anything, e.g., a person, document, organization, etc.

1. Specify a definition that describes the simplified data structure and maps to SPARQL
    clauses.
2. Generate a SPARQL CONSTRUCT query from the definition.
3. Execute the SPARQL CONSTRUCT query against a VIVO SPARQL API endpoint.
4. Transform the resulting RDF graph into a simplified (python) data structure.
5. Serialize the simplified data structure to JSON, XML, YAML, etc.

Example definition:

	person_definition = {
	  #?subj is the subject of the definition.  When the definition is processed, it
	  #will be bound (with BIND) to a uri.
	  #"where" are clauses that should be included in the WHERE. 
        "where": "?subj a foaf:Person .",
        #fields for the subject.
        "fields": {
            "name": {
                #where clauses for the field.
                #both ?subj and ?obj will be replaced with unique variable names.
                "where": "?subj rdfs:label ?obj ."
            },
            "researchArea": {
                #Multiple clauses can be provided.
                "where": """
                            ?subj vivo:hasResearchArea ?ra .
                            ?ra rdfs:label ?obj .
                         """,
                #If optional, where clauses will be wrapped in OPTIONAL.
                "optional": True,
                #Indicates that should be a list, even if there is only a single value.
                "list": True
            },
           "geographicFocus": {
                "where": """
                            ?subj vivo:geographicFocus ?gf .
                            ?gf rdfs:label ?obj .
                         """,
                "optional": True,
                "list": True
           	}, 
            "publications": {
                #A where that traversed multiple relationships.
                "where": """
                            ?subj vivo:relatedBy ?aship .
                            ?aship a vivo:Authorship .
                            ?aship vivo:relates ?obj .
                         """,
                #Definition specifies a definition for a child subject.
                #This is defined elsewhere.
                "definition": document_summary_definition,
                "optional": True,
                "list": True
            }
        }
    }
    
results in (omitting namespace declaration):

    CONSTRUCT
    {
        ?v0 :type ?v1 .
        ?v0 :researchArea ?v2 .
        ?v0 :researchArea rdf:List .
        ?v0 :geographicFocus ?v3 .
        ?v0 :geographicFocus rdf:List .
        ?v0 :name ?v4 .
        ?v0 :publications ?v5 .
        ?v0 :publications rdf:List .
        ?v5 :type ?v6 .
        ?v5 :journal ?v7 .
        ?v7 :type ?v8 .
        ?v7 :title ?v9 .
        ?v5 :issue ?v10 .
        ?v5 :title ?v11 .
    }
    WHERE
    {
        BIND ((subj-ns:n115)  AS ?v0 )
        {
            ?v0 a foaf:Person .
            ?v0 vitro:mostSpecificType ?v1 .
            ?v0 rdfs:label ?v4 .
        }
        OPTIONAL
        {
            ?v0 vivo:hasResearchArea ?ra .
            ?ra rdfs:label ?v2 .
        }
        OPTIONAL
        {
            ?v0 vivo:geographicFocus ?gf .
            ?gf rdfs:label ?v3 .
        }
        OPTIONAL
        {
            ?v0 vivo:relatedBy ?aship .
            ?aship a vivo:Authorship .
            ?aship vivo:relates ?v5 .
            ?v5 vitro:mostSpecificType ?v6 .
            ?v5 a bibo:Document .
            ?v5 rdfs:label ?v11 .
            OPTIONAL
            {
                ?v5 vivo:hasPublicationVenue ?v7 .
                ?v7 vitro:mostSpecificType ?v8 .
                ?v7 a bibo:Journal .
                ?v7 rdfs:label ?v9 .
            }
            OPTIONAL
            {
                ?v5 bibo:issue ?v10 .
            }
        }
    }
        
and executed against a test data source results in the following (omitting namespaces):

      subj-ns:n115 :geographicFocus rdf:List,
            "New Jersey"@en ;
        :name "Littman, Justin "^^xsd:string ;
        :publications subj-ns:n6493,
            subj-ns:n7738,
            subj-ns:n886,
            rdf:List ;
        :researchArea rdf:List,
            "Economics"^^xsd:string,
            "Philosophy"^^xsd:string ;
        :type vivo:Librarian .

    subj-ns:n5080 :title "Bar Journal"^^xsd:string ;
        :type bibo:Journal .

    subj-ns:n5258 :title "Foo Journal"^^xsd:string ;
        :type bibo:Journal .

    subj-ns:n6493 :journal subj-ns:n5080 ;
        :title "My Second Academic Article"^^xsd:string ;
        :type bibo:AcademicArticle .

    subj-ns:n7738 :issue "3"^^xsd:string ;
        :journal subj-ns:n5258 ;
        :title "My First Academic Article"^^xsd:string ;
        :type bibo:AcademicArticle .

    subj-ns:n886 :title "My blog posting"^^xsd:string ;
        :type vivo:BlogPosting .


and transformed to the simplified data structure:

    {u'researchArea': [u'Philosophy', u'Economics'], u'name': u'Littman, Justin ', 'uri': 'http://vivo.gwu.edu/individual/n115', u'publications': [{u'type': u'BlogPosting', 'uri': 'http://vivo.gwu.edu/individual/n886', u'title': u'My blog posting'}, {u'journal': {u'type': u'', 'uri': 'http://vivo.gwu.edu/individual/n5080', u'title': u'Bar Journal'}, u'type': u'', 'uri': 'http://vivo.gwu.edu/individual/n6493', u'title': u'My Second Academic Article'}, {u'issue': u'3', u'journal': {u'type': u'', 'uri': 'http://vivo.gwu.edu/individual/n5258', u'title': u'Foo Journal'}, u'type': u'', 'uri': 'http://vivo.gwu.edu/individual/n7738', u'title': u'My First Academic Article'}], u'geographicFocus': [u'New Jersey'], u'type': u'Librarian'}
	

and serialized to JSON:

    {
        "researchArea": [
            "Philosophy", 
            "Economics"
        ], 
        "name": "Littman, Justin ", 
        "uri": "http://vivo.gwu.edu/individual/n115", 
        "publications": [
            {
                "type": "BlogPosting", 
                "uri": "http://vivo.gwu.edu/individual/n886", 
                "title": "My blog posting"
            }, 
            {
                "journal": {
                    "type": "", 
                    "uri": "http://vivo.gwu.edu/individual/n5080", 
                    "title": "Bar Journal"
                }, 
                "type": "", 
                "uri": "http://vivo.gwu.edu/individual/n6493", 
                "title": "My Second Academic Article"
            }, 
            {
                "issue": "3", 
                "journal": {
                    "type": "", 
                    "uri": "http://vivo.gwu.edu/individual/n5258", 
                    "title": "Foo Journal"
                }, 
                "type": "", 
                "uri": "http://vivo.gwu.edu/individual/n7738", 
                "title": "My First Academic Article"
            }
        ], 
        "geographicFocus": [
            "New Jersey"
        ], 
        "type": "Librarian"
    }

or yaml:

    geographicFocus: [New Jersey]
    name: 'Littman, Justin '
    publications:
    -   journal: {title: Bar Journal, type: '', uri: 'http://vivo.gwu.edu/individual/n5080'}
        title: My Second Academic Article
        type: ''
        uri: http://vivo.gwu.edu/individual/n6493
    - {title: My blog posting, type: BlogPosting, uri: 'http://vivo.gwu.edu/individual/n886'}
    -   issue: '3'
        journal: {title: Foo Journal, type: '', uri: 'http://vivo.gwu.edu/individual/n5258'}
        title: My First Academic Article
        type: ''
        uri: http://vivo.gwu.edu/individual/n7738
    researchArea: [Economics, Philosophy]
    type: Librarian
    uri: http://vivo.gwu.edu/individual/n115

or xml:

    <?xml version="1.0" ?>
    <librarian uri="http://vivo.gwu.edu/individual/n115">
    <researcharea>Economics</researcharea>
    <researcharea>Philosophy</researcharea>
    <name>Littman, Justin </name>
    <publications>
        <blogposting uri="http://vivo.gwu.edu/individual/n886">
            <title>My blog posting</title>
        </blogposting>
        <academicarticle uri="http://vivo.gwu.edu/individual/n6493">
            <journal uri="http://vivo.gwu.edu/individual/n5080">
                <title>Bar Journal</title>
            </journal>
            <title>My Second Academic Article</title>
        </academicarticle>
        <academicarticle uri="http://vivo.gwu.edu/individual/n7738">
            <journal uri="http://vivo.gwu.edu/individual/n5258">
                <title>Foo Journal</title>
            </journal>
            <issue>3</issue>
            <title>My First Academic Article</title>
        </academicarticle>
    </publications>
    <geographicfocus>New Jersey</geographicfocus>
    </librarian>

### For lists

Note that:

* individuals can be lists of anything with relationships to anything, e.g., persons with positions in a department.
* lists support pagination (via offsets and limits).
* lists support ordering.

1. Specify a definition that describes the simplified data structure and maps to SPARQL
    clauses and provide an optional limit and offset.
2. Generate a SPARQL CONSTRUCT, SELECT, and SELECT count query from the definition.
     * The SELECT query is used to order the list since order is not preserved in the CONSTRUCT.
     * The SELECT count is used to provide a total count for the list (i.e., without limits and offsets).
3. Execute the queries against a VIVO SPARQL API endpoint.
4. Based on the order of results from SELECT query, transform the RDF graph from the CONSTRUCT into a simplified (python) data structure and add the count returned by the SELECT count query.
5. Serialize the simplified data structure to JSON, XML, YAML, etc.

Example definition:

    definition = {
        #"where" specifies how the list is selected, in this
        #case individuals that are related to a position.
        "where": """
                    ?subj vivo:relatedBy ?pos .
                    ?pos a vivo:Position .
                    ?pos vivo:relates ?obj .
                 """,
        #"list_definition" specifies the results, in this
        #case a summary for a person.
        "list_definition": {
            "where": "?subj a foaf:Person .",
            "fields": {
                "name": {
                    "where": "?subj rdfs:label ?obj .",
                    #"order" specifies the fields to be used
                    #for ordering. Number the fields starting
                    #with 1.
                    "order": 1,
                    #"order_asc" specifies whether the list is
                    #ordered ascending or descending. If omitted,
                    #the default is ascending.
                    "order_asc": True
                }
            }
        }
    }
    
results in (omitting namespace declaration):

    CONSTRUCT
    {
        ?v0 :result ?v1 .
        ?v1 :type ?v2 .
        ?v1 :name ?v3 .
    }
    WHERE
    {
        {
            SELECT DISTINCT ?v0 ?v1 ?v2 ?v3
            WHERE
            {
                BIND ((subj-ns:n3360)  AS ?v0 )
                {
                    ?v0 vivo:relatedBy ?pos .
                    ?pos a vivo:Position .
                    ?pos vivo:relates ?v1 .
                    ?v1 a foaf:Person .
                    ?v1 vitro:mostSpecificType ?v2 .
                    ?v1 rdfs:label ?v3 .
                }
            }
            ORDER BY ASC(?v3)
            LIMIT 4
            OFFSET 2
        }
    }
    
and 

    SELECT DISTINCT ?v1
    WHERE
    {
        BIND ((subj-ns:n3360)  AS ?v0 )
        {
            ?v0 vivo:relatedBy ?pos .
            ?pos a vivo:Position .
            ?pos vivo:relates ?v1 .
            ?v1 a foaf:Person .
            ?v1 vitro:mostSpecificType ?v2 .
            ?v1 rdfs:label ?v3 .
        }
    }
    ORDER BY ASC(?v3)
    LIMIT 3
    OFFSET 2

and

    SELECT (COUNT(DISTINCT ?v1) as ?count)
    WHERE
    {
        BIND ((subj-ns:n3360)  AS ?v0 )
        {
            ?v0 vivo:relatedBy ?pos .
            ?pos a vivo:Position .
            ?pos vivo:relates ?v1 .
            ?v1 a foaf:Person .
            ?v1 vitro:mostSpecificType ?v2 .
            ?v1 rdfs:label ?v3 .
        }
    }


and executed against a test data source results in the following (omitting namespaces):

     subj-ns:n3360 :result subj-ns:n1941,
            subj-ns:n716,
            <http://vivo.mydomain.edu/person-53e4096d5bf17f776300c4e2e8d237ee> .

    subj-ns:n1941 :name "Kaplan, Beth "^^xsd:string ;
        :type vivo:Librarian .

    subj-ns:n716 :name "Kerchner, Dan "^^xsd:string ;
        :type vivo:Librarian .

    <http://vivo.mydomain.edu/person-53e4096d5bf17f776300c4e2e8d237ee> :name "Justin Littman" ;
        :type vivo:Librarian .


and transformed to the simplified data structure:

    {'count': u'10', 'limit': 3, 'list': [{u'type': u'Librarian', 'uri': 'http://vivo.mydomain.edu/person-53e4096d5bf17f776300c4e2e8d237ee', u'name': u'Justin Littman'}, {u'type': u'Librarian', 'uri': 'http://vivo.mydomain.edu/individual/n1941', u'name': u'Kaplan, Beth '}, {u'type': u'Librarian', 'uri': 'http://vivo.mydomain.edu/individual/n716', u'name': u'Kerchner, Dan '}], 'offset': 2}

and serialized to JSON:

    {
        "count": 10, 
        "limit": 3, 
        "list": [
            {
                "type": "Librarian", 
                "uri": "http://vivo.mydomain.edu/person-53e4096d5bf17f776300c4e2e8d237ee", 
                "name": "Justin Littman"
            }, 
            {
                "type": "Librarian", 
                "uri": "http://vivo.mydomain.edu/individual/n1941", 
                "name": "Kaplan, Beth "
            }, 
            {
                "type": "Librarian", 
                "uri": "http://vivo.mydomain.edu/individual/n716", 
                "name": "Kerchner, Dan "
            }
        ], 
        "offset": 2
    }

or yaml:

    count: 10
    limit: 3
    list:
    - {name: Justin Littman, type: Librarian, uri: 'http://vivo.mydomain.edu/person-53e4096d5bf17f776300c4e2e8d237ee'}
    - {name: 'Kaplan, Beth ', type: Librarian, uri: 'http://vivo.mydomain.edu/individual/n1941'}
    - {name: 'Kerchner, Dan ', type: Librarian, uri: 'http://vivo.mydomain.edu/individual/n716'}
    offset: 2
    
or xml:

    <?xml version="1.0" ?>
    <list count="10" limit="3" offset="2">
        <librarian uri="http://vivo.mydomain.edu/person-53e4096d5bf17f776300c4e2e8d237ee">
            <name>Justin Littman</name>
        </librarian>
        <librarian uri="http://vivo.mydomain.edu/individual/n1941">
            <name>Kaplan, Beth </name>
        </librarian>
        <librarian uri="http://vivo.mydomain.edu/individual/n716">
            <name>Kerchner, Dan </name>
        </librarian>
    </list>