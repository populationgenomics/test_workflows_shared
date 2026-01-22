from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path, hail_batch


def say_hi_job(
    sequencing_group: SequencingGroup,
    job_attrs: dict[str, str],
    output_file_path: Path,
) -> Job:
    b = hail_batch.get_batch()
    job = b.new_job(name=f'Say Hi: {sequencing_group.id}', attributes=job_attrs)

    job.command(f"""
    echo "This is a hello from sequencing_group {sequencing_group.id}" > {job.sayhi}
    """)

    logger.info('-----PRINT SAY HI-----')
    logger.info(output_file_path)
    b.write_output(job.sayhi, output_file_path)

    return job
