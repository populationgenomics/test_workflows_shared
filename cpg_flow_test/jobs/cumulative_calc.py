from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path, config, hail_batch


def cumulative_calc_job(
    sequencing_group: SequencingGroup,
    input_file_path: Path,
    job_attrs: dict[str, str],
    output_file_path: Path,
) -> Job:
    b = hail_batch.get_batch()
    job = b.new_job(name=f'Cumulative Calc: {sequencing_group.id}', attributes=job_attrs)
    job.image(config.config_retrieve(['images', 'ubuntu']))

    primes_path = b.read_input(input_file_path)

    job.command(f"""
    primes=($(cat {primes_path}))
    csum=0
    cumulative=()
    for prime in "${{primes[@]}}"; do
        ((csum += prime))
        cumulative+=("$csum")
    done
    echo "${{cumulative[@]}}" > {job.cumulative}
    """)

    logger.info('-----PRINT CUMULATIVE-----')
    logger.info(output_file_path)
    b.write_output(job.cumulative, output_file_path)

    return job
