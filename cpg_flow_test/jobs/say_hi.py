from loguru import logger

from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job


def say_hi(
    b: Batch,
    sequencing_group: SequencingGroup,
    output_file_path: str,
) -> list[Job]:
    title = f'Say Hi: {sequencing_group.id}'
    job = b.new_job(name=title)

    cmd = f"""
    echo "This is a hello from sequencing_group {sequencing_group.id}" > {job.sayhi}
    """

    job.command(cmd)

    logger.info('-----PRINT SAY HI-----')
    logger.info(output_file_path)
    b.write_output(job.sayhi, output_file_path)

    return job
