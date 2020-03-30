#!/bin/bash
config=$(envsubst < app.yaml)
echo "$config" > app.yaml