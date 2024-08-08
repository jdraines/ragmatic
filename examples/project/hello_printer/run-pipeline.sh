#!/bin/bash
# NOTE: this helper script assumes you have open ai credentials stored in ~/.credentials/openai-api-key
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export OPENAI_API_KEY=$(cat ~/.credentials/openai-api-key)
OPENAI_API_KEY=$OPENAI_API_KEY ragmatic run ingest-python-codebase \
    --config $SCRIPT_DIR/example-config.yaml