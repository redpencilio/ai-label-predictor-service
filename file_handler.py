from escape_helpers import sparql_escape_uri, sparql_escape_string, sparql_escape_int, sparql_escape_datetime
from helpers import query, update, generate_uuid
import os
from string import Template
from pytz import timezone
from datetime import datetime

TIMEZONE = timezone("Europe/Brussels")
FILE_BASE_URI = "http://file/files/"
MU_APPLICATION_GRAPH = os.environ.get('MU_APPLICATION_GRAPH')


def construct_insert_file_query(virtualFile, physicalFile):
    """
    Construct SPARQL query for inserting a file
    :param virtualFile: virtual file information
    :param physicalFile: physical file information
    :return: string containing SPARQL query
    """
    queryTemplate = Template("""
    PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
    PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
    PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>
    PREFIX dct: <http://purl.org/dc/terms/>
    PREFIX dbpedia: <http://dbpedia.org/ontology/>
    INSERT DATA {
        GRAPH $graph {
            $uri a nfo:FileDataObject ;
                mu:uuid $uuid ;
                nfo:fileName $name ;
                dct:format $mimetype ;
                dct:created $created ;
                nfo:fileSize $size ;
                dbpedia:fileExtension $extension .
            $physical_uri a nfo:FileDataObject ;
                mu:uuid $physical_uuid ;
                nfo:fileName $physical_name ;
                dct:format $mimetype ;
                dct:created $created ;
                nfo:fileSize $size ;
                dbpedia:fileExtension $extension ;
                nie:dataSource $uri .
        }
    }
    """)

    return queryTemplate.substitute(
        graph=sparql_escape_uri("http://mu.semte.ch/application"),
        uri=sparql_escape_uri(virtualFile["uri"]),
        uuid=sparql_escape_string(virtualFile["uuid"]),
        name=sparql_escape_string(virtualFile["name"]),
        mimetype=sparql_escape_string(virtualFile["mimetype"]),
        created=sparql_escape_datetime(virtualFile["created"]),
        size=sparql_escape_int(virtualFile["size"]),
        extension=sparql_escape_string(virtualFile["extension"]),
        physical_uri=sparql_escape_uri(physicalFile["uri"]),
        physical_uuid=sparql_escape_string(physicalFile["uuid"]),
        physical_name=sparql_escape_string(physicalFile["name"])

    )


def construct_get_file_by_id(file_id):
    """
    Construct query to get file based on file id
    :param file_id: string:file id
    :return: string:query
    """
    query_template = Template("""
    PREFIX mu: <http://mu.semte.ch/vocabularies/core/>
    PREFIX nfo: <http://www.semanticdesktop.org/ontologies/2007/03/22/nfo#>
    PREFIX nie: <http://www.semanticdesktop.org/ontologies/2007/01/19/nie#>
    SELECT (?phys_file AS ?uri)
    WHERE {
        GRAPH $graph {
            ?virt_file a nfo:FileDataObject ;
                mu:uuid $uuid .
            ?phys_file a nfo:FileDataObject ;
                nie:dataSource ?virt_file .
        }
    }
    LIMIT 1
    """)
    return query_template.substitute(
        graph=sparql_escape_uri(MU_APPLICATION_GRAPH),
        uuid=sparql_escape_string(file_id))


def get_file_by_id(id):
    return query(construct_get_file_by_id(id))


def postfile(filePath, fileName):
    """
    Store a file in data store
    :param filePath: path to file
    :param fileName: name of physical file
    :return: dict{ string:virtual file id, string:virtual file uri}
    """
    fileSize = os.path.getsize(filePath)
    extension = fileName.split('.')[-1]

    virtualFile = {
        "created": datetime.now(TIMEZONE),
        "extension": extension,
        "uuid": generate_uuid(),
        "mimetype": "application/json",
        "size": fileSize
    }

    virtualFile["uri"] = FILE_BASE_URI + virtualFile["uuid"]
    virtualFile["name"] = virtualFile["uuid"]

    physicalFile = {
        "extension": extension,
        "name": fileName,
        "uuid": fileName.split('.')[0],
        "uri": filePath.replace("/share/", "share://")

    }

    queryString = construct_insert_file_query(virtualFile, physicalFile)

    update(queryString)

    return {"id": virtualFile["uuid"], "uri": virtualFile["uri"]}
