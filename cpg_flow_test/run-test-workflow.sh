#!/bin/bash

DEFAULT_IMAGE_REPOSITORY="australia-southeast1-docker.pkg.dev/cpg-common/images"
IMAGE_TAG="cpg_flow:0.1.3"
IMAGE_PATH="$DEFAULT_IMAGE_REPOSITORY/$IMAGE_TAG"

PATH_OVERRIDE=0
CONFIG_PATH="configs/default_config.toml"
DATASET="fewgenomes"

DRY_RUN=0
SKIP_ARG=0

ARGS=("$@")

for i in "${!ARGS[@]}"; do
  arg="${ARGS[$i]}"
  arg2="${ARGS[$i+1]}"

  if [ $SKIP_ARG -eq 1 ]; then
    SKIP_ARG=0
    continue
  fi

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
      echo "${GREEN}$0 --image \"cpg_flow:0.1.3\"${RESET}"
      echo "Valid tags can be found from the most recent ${YELLOW}cpg-flow${RESET} docker deployment runs on Github:"
      echo "${YELLOW}https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml${RESET}"
      exit 1
    fi
    echo "Using image path (img:tag): $IMAGE_PATH"
    SKIP_ARG=1
  elif [[ "$arg" == "--config" ]]; then
    CONFIG_PATH="$arg2"
    echo "Using config file: $CONFIG_PATH"
    SKIP_ARG=1
  elif [[ "$arg" == "--dataset" ]]; then
    DATASET="$arg2"
    echo "Using dataset: $DATASET"
    SKIP_ARG=1
  elif [[ "$arg" == "--dry-run" ]]; then
    echo "Dry run enabled"
    DRY_RUN=1
  else
    RED=$(tput setaf 1)
    RESET=$(tput sgr0)
    echo "${RED}Invalid argument: $arg${RESET}"
    echo "Usage: $0 [--image <image_repo_url>:<tag>] [--config <config_file_path>] [--dataset <dataset_name>] [--dry-run]"
    echo "e.g"
    GREEN=$(tput setaf 2)
    echo "${GREEN}$0 --image-tag \"cpg_flow:0.1.1\" --config \"custom_config.toml\" --dataset \"test-umbrella\" --dry-run${RESET}"
    exit 1
  fi
done

if [ $PATH_OVERRIDE -eq 0 ]; then
  echo "Using default image path (img:tag): $IMAGE_PATH"
fi

# Check for unstaged changes in the git repo
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

# Check that the docker image can be pulled
if which docker >/dev/null; then
  if docker manifest inspect "$IMAGE_PATH" > /dev/null 2>&1; then
    echo "Docker image $IMAGE_PATH exists."
  else
    if [[ $? -eq 137 ]]; then
      echo "Docker command was killed. Skipping image check."
    else
      echo "Docker image $IMAGE_PATH does not exist. Please build the image before running this script."
      exit 1
    fi
  fi
else
  echo "Docker is not installed. Skipping image check."
fi

echo "analysis-runner
  --config "$CONFIG_PATH"
  --dataset "$DATASET"
  --description "cpg-flow_test"
  --access-level "test"
  --output-dir "cpg-flow_test"
  --config "$CONFIG_PATH"
  workflow.py"

if [ $DRY_RUN -eq 1 ]; then
  echo "Dry run complete. Exiting..."
  exit 0
fi

echo "Executing the analysis-runner command..."

analysis-runner \
  --image "$IMAGE_PATH" \
  --dataset "$DATASET" \
  --description "cpg-flow_test" \
  --access-level "test" \
  --output-dir "cpg-flow_test" \
  --config "$CONFIG_PATH" \
  workflow.py
