from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils.config import config_retrieve
from cpg_utils.hail_batch import get_batch
from hailtop.batch import Batch
from hailtop.batch.job import Job
from loguru import logger


def cumulative_calc_job(
    sequencing_group: SequencingGroup,
    input_file_path: str,
    job_attrs: dict[str, str],
    output_file_path: str,
) -> list[Job]:
    b = get_batch()
    title = f'Cumulative Calc: {sequencing_group.id}'
    job = b.new_job(name=title, attributes=job_attrs)
    job.image(config_retrieve['workflow', 'driver_image'])
    primes_path = b.read_input(input_file_path)

    cmd = f"""
    primes=($(cat {primes_path}))
    csum=0
    cumulative=()
    for prime in "${{primes[@]}}"; do
        ((csum += prime))
        cumulative+=("$csum")
    done
    echo "${{cumulative[@]}}" > {job.cumulative}
    """

    job.command(cmd)

    logger.info('-----PRINT CUMULATIVE-----')
    logger.info(output_file_path)
    b.write_output(job.cumulative, output_file_path)

    return job
