from typing import Any

from cpg_flow.stage import Stage, StageInput
from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils.config import config_retrieve
from cpg_utils.hail_batch import get_batch
from hailtop.batch import Batch
from hailtop.batch.job import Job
from loguru import logger


def filter_evens_job(
    sequencing_groups: list[SequencingGroup],
    input_files: dict[str, dict[str, Any]],
    job_attrs: dict[str, str],
    sg_outputs: dict[str, dict[str, Any]],
    output_file_path: str,
) -> list[Job]:

    b = get_batch()
    title = 'Filter Evens'

    # Compute the no evens list for each sequencing group
    sg_jobs = []
    sg_output_files = []
    for sg in sequencing_groups:  # type: ignore
        job = b.new_job(name=title + ': ' + sg.id, attributes=job_attrs)
        job.image(config_retrieve['workflow', 'driver_image'])
        input_file_path = input_files[sg.id]['cumulative']
        no_evens_input_file = b.read_input(input_file_path)
        no_evens_output_file_path = str(sg_outputs[sg.id])
        sg_output_files.append(no_evens_output_file_path)

        cmd = f"""
        numbers=($(cat {no_evens_input_file}))
        result=()
        for num in "${{numbers[@]}}"; do
            if (( num % 2 != 0 )); then
                result+=("$num")
            fi
        done
        echo "{sg.id}: ${{result[@]}}" > {job.sg_no_evens_file}
        """

        job.command(cmd)
        b.write_output(job.sg_no_evens_file, no_evens_output_file_path)
        sg_jobs.append(job)

    # Merge the no evens lists for all sequencing groups into a single file
    job = b.new_job(name=title, attributes=job_attrs)
    job.image(config_retrieve['workflow', 'driver_image'])
    job.depends_on(*sg_jobs)
    inputs = ' '.join([b.read_input(f) for f in sg_output_files])
    job.command(f'cat {inputs} >> {job.no_evens_file}')
    b.write_output(job.no_evens_file, output_file_path)

    logger.info('-----PRINT NO EVENS-----')
    logger.info(output_file_path)

    all_jobs = [job, *sg_jobs]

    return all_jobs
