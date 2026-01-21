from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils.config import config_retrieve
from cpg_utils.hail_batch import get_batch
from hailtop.batch.job import Job
from loguru import logger


def say_hi_job(
    sequencing_group: SequencingGroup,
    job_attrs: dict[str, str],
    output_file_path: str,
) -> list[Job]:
    b = get_batch()
    title = f'Say Hi: {sequencing_group.id}'
    job = b.new_job(name=title, attributes=job_attrs)
    job.image(config_retrieve(['workflow', 'driver_image']))

    cmd = f"""
    echo "This is a hello from sequencing_group {sequencing_group.id}" > {job.sayhi}
    """

    job.command(cmd)

    logger.info('-----PRINT SAY HI-----')
    logger.info(output_file_path)
    b.write_output(job.sayhi, output_file_path)

    return job
