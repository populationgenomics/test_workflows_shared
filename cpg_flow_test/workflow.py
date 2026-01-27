#!/usr/bin/env python3
import os
import sys
from pathlib import Path

from cpg_flow.workflow import run_workflow
from cpg_utils.config import set_config_paths
from stages import BuildAPrimePyramid, CumulativeCalc, FilterEvens, GeneratePrimes, SayHi, SayHiC, SayHiD, SayHiB

TMP_DIR = os.getenv('TMP_DIR')
# CONFIG_FILE = str(Path(__file__).parent / 'config.toml')

message = "Hello, Hail Batch! I'm CPG flow, nice to meet you."


def run_cpg_flow(dry_run=False):
    workflow = [GeneratePrimes, SayHi, SayHiB, SayHiC, SayHiD]

    config_paths = os.environ['CPG_CONFIG_PATH'].split(',')
    print(f'CPG_CONFIG_PATHS: {config_paths}')

    # Inserting after the "defaults" config, but before user configs:
    # set_config_paths(config_paths[:1] + [CONFIG_FILE] + config_paths[1:])
    set_config_paths(config_paths)
    run_workflow(name="test-naming-changes", stages=workflow, dry_run=dry_run)


def validate_batch_workflow():
    if not os.path.exists(f'{TMP_DIR}/out.txt'):
        print('Batch workflow failed')
        sys.exit(1)

    success = False
    with open(f'{TMP_DIR}/out.txt', 'r') as f:
        success = f.read().strip() == message

    print(f'Batch workflow {"succeeded" if success else "failed"}')
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    run_cpg_flow()
