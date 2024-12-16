#!/bin/bash

DEFAULT_IMAGE_TAG="images/cpg_flow:0.1.0-alpha.9"

# If there is a command line argument, use it as the image tag
if [[ -n $1 ]]; then
  echo "Using image tag: $1"
  IMAGE_TAG=$1
else
  echo "Using default image tag: $DEFAULT_IMAGE_TAG"
  IMAGE_TAG=$DEFAULT_IMAGE_TAG
fi

# Check for unstaged changes in the git repo
if [[ -n $(git status -s) ]]; then
  echo "There are unstaged changes in the git repo. Please commit or stash them before running this script."
  exit 1
fi

# Check for uncommitted changes in the git repo
if [[ -n $(git diff) ]]; then
  echo "There are uncommitted changes in the git repo. Please commit or stash them before running this script."
  exit 1
fi

echo "analysis-runner
  --image "australia-southeast1-docker.pkg.dev/cpg-common/$IMAGE_TAG"
  --dataset "fewgenomes"
  --description "cpg-flow_test"
  --access-level "test"
  --output-dir "cpg-flow_test"
  --config "config.toml"
  workflow.py"

analysis-runner \
  --image "australia-southeast1-docker.pkg.dev/cpg-common/$IMAGE_TAG" \
  --dataset "fewgenomes" \
  --description "cpg-flow_test" \
  --access-level "test" \
  --output-dir "cpg-flow_test" \
  --config "config.toml" \
  workflow.py
