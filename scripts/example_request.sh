#!/bin/bash
curl --data-ascii '{"Arts":0.9,"Autos":0.5}' -H "Content-Type:application/json" "http://127.0.0.1:4355/nytimes/mostpopular/personalize?limit=20"
