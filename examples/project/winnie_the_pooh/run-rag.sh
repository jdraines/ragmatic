#!/bin/bash
# NOTE: this helper script assumes you have open ai credentials stored in ~/.credentials/openai-api-key
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export OPENAI_API_KEY=$(cat ~/.credentials/openai-api-key)
OPENAI_API_KEY=$OPENAI_API_KEY ragmatic rag-query \
    -v local_documents_path=./book \
    -v n_nearest=3 \
    --query "Who found Eeyore's tail? Can you quote the text that describes the event?"
