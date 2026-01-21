import os
import sys

from stages import BuildAPrimePyramid, CumulativeCalc, FilterEvens, GeneratePrimes, SayHi

from cpg_flow.workflow import run_workflow
from cpg_utils.config import set_config_paths

TMP_DIR = os.getenv('TMP_DIR')

message = "Hello, Hail Batch! I'm CPG flow, nice to meet you."


def run_cpg_flow(dry_run: bool = False):
    workflow = [GeneratePrimes, CumulativeCalc, FilterEvens, BuildAPrimePyramid, SayHi]

    config_paths = os.environ['CPG_CONFIG_PATH'].split(',')
    print(f'CPG_CONFIG_PATHS: {config_paths}')

    # Inserting after the "defaults" config, but before user configs:
    set_config_paths(config_paths)
    run_workflow(name='test_workflows_shared', stages=workflow, dry_run=dry_run)


def validate_batch_workflow():
    if not os.path.exists(f'{TMP_DIR}/out.txt'):
        print('Batch workflow failed')
        sys.exit(1)

    success = False
    with open(f'{TMP_DIR}/out.txt') as f:
        success = f.read().strip() == message

    print(f'Batch workflow {"succeeded" if success else "failed"}')
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    run_cpg_flow()
