curl -X DELETE "http://localhost:9200/tagz" 

curl -X PUT "http://localhost:9200/tagz" -d '
{
    "mappings" : {
        "files" : {
            "properties" : {
                "path" : {
                    "type" : "string",
                    "index" : "not_analyzed" 
                }
            }
        }
    }
}
'

echo "\n"
echo "Index tagz for ElasticSearch created"
echo "You may now proceed to index your files..."
