#!/bin/bash

DEFAULT_IMAGE_REPOSITORY="australia-southeast1-docker.pkg.dev/cpg-common/images"
IMAGE_TAG="cpg_flow:0.1.0-alpha.14"
IMAGE_PATH="$DEFAULT_IMAGE_REPOSITORY/$IMAGE_TAG"

PATH_OVERRIDE=0

for arg in "$@"; do
  if [[ "$arg" == "--image" ]]; then

    PATH_OVERRIDE=1

    IMAGE_PATH=$2

    # Make sure the image tag is of the format <image>:<tag>
    if [[ ! $IMAGE_PATH =~ ^[^:]+:[^:]+$ ]]; then
      RED=$(tput setaf 1)
      RESET=$(tput sgr0)
      echo "${RED}Invalid path/tag: $IMAGE_PATH${RESET}"
      echo "Usage: $0 [--image <image_repo_url>:<tag>]"
      echo "e.g"
      GREEN=$(tput setaf 2)
      YELLOW=$(tput setaf 3)
      echo "${GREEN}$0 --image \"cpg_flow:0.1.0-alpha.14\"${RESET}"
      echo "Valid tags can be found from the most recent ${YELLOW}cpg-flow${RESET} docker deployment runs on Github:"
      echo "${YELLOW}https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml${RESET}"
      exit 1
    fi
    echo "Using image path (img:tag): $IMAGE_PATH"
    break
  else
    RED=$(tput setaf 1)
    RESET=$(tput sgr0)
    echo "${RED}Invalid argument: $arg${RESET}"
    echo "Usage: $0 [--image <image_repo_url>:<tag>]"
    echo "e.g"
    GREEN=$(tput setaf 2)
    echo "${GREEN}$0 --image-tag \"cpg_flow:0.1.0-alpha.9\"${RESET}"
    exit 1
  fi
done

if [ $PATH_OVERRIDE -eq 0 ]; then
  echo "Using default image path (img:tag): $IMAGE_PATH"
fi

Check for unstaged changes in the git repo
if [[ -n $(git status -s) ]]; then
  RED=$(tput setaf 1)
  RESET=$(tput sgr0)
  echo "${RED}Hail cannot read your unstaged changes and there are unstaged changes in the git repo. Please commit or stash them before running this script.${RESET}"
  exit 1
fi

# Check for uncommitted changes in the git repo
if [[ -n $(git diff) ]]; then
  echo "${RED}Hail cannot read your uncommitted changes and there are uncommitted changes in the git repo. Please commit or stash them before running this script.${RESET}"
  exit 1
fi

echo "analysis-runner
  --image "$IMAGE_PATH"
  --dataset "fewgenomes"
  --description "cpg-flow_test"
  --access-level "test"
  --output-dir "cpg-flow_test"
  --config "config.toml"
  workflow.py"

analysis-runner \
  --image "$IMAGE_PATH" \
  --dataset "fewgenomes" \
  --description "cpg-flow_test" \
  --access-level "test" \
  --output-dir "cpg-flow_test" \
  --config "config.toml" \
  workflow.py
