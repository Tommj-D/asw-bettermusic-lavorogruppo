#!/bin/bash

# cancella alcune recensioni (ID 2 e ID 6) tramite API Gateway

echo "# cancellazione recensione 2"
curl -s -X DELETE "http://localhost:8080/recensioni/recensioni/2" | jq .
echo

echo "# cancellazione recensione 6"
curl -s -X DELETE "http://localhost:8080/recensioni/recensioni/6" | jq .
echo