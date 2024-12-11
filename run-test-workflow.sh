#!/bin/bash

echo analysis-runner \
    --image "australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:0.1.0-alpha.9" \
    --dataset "fewgenomes" \
    --description "cpg-flow_test" \
    --access-level "test" \
    --output-dir "cpg-flow_test" \
    --config "config.toml" \
    workflow.py

analysis-runner \
    --image "australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:0.1.0-alpha.9" \
    --dataset "fewgenomes" \
    --description "cpg-flow_test" \
    --access-level "test" \
    --output-dir "cpg-flow_test" \
    --config "config.toml" \
    workflow.py
