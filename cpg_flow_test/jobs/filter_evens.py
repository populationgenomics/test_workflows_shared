from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_flow.utils import dependency_handler
from cpg_utils import Path, config, hail_batch


def filter_evens_job(
    sequencing_groups: list[SequencingGroup],
    input_files: dict[str, dict[str, Path]],
    job_attrs: dict[str, str],
    sg_outputs: dict[str, dict[str, Path] | Path],
) -> list[Job]:
    b = hail_batch.get_batch()
    title = 'Filter Evens'

    # Compute the no evens list for each sequencing group
    all_jobs = []
    sg_output_files = []
    for sg in sequencing_groups:
        job = b.new_bash_job(name=f'{title}: {sg.id}', attributes=job_attrs)
        job.image(config.config_retrieve(['images', 'ubuntu']))
        input_file_path = input_files[sg.id]['cumulative']
        sg_output_files.append(sg_outputs[sg.id])

        job.command(f"""
        numbers=($(cat {b.read_input(input_file_path)}))
        result=()
        for num in "${{numbers[@]}}"; do
            if (( num % 2 != 0 )); then
                result+=("$num")
            fi
        done
        echo "{sg.id}: ${{result[@]}}" > {job.sg_no_evens_file}
        """)

        b.write_output(job.sg_no_evens_file, sg_outputs[sg.id])
        all_jobs.append(job)

    # Merge the no evens lists for all sequencing groups into a single file
    job = b.new_bash_job(name=title, attributes=job_attrs)
    job.image(config.config_retrieve(['images', 'ubuntu']))

    dependency_handler(job, all_jobs)

    inputs = ' '.join([b.read_input(f) for f in sg_output_files])
    job.command(f'cat {inputs} >> {job.no_evens_file}')
    b.write_output(job.no_evens_file, sg_outputs['no_evens'])

    logger.info('-----PRINT NO EVENS-----')
    logger.info(sg_outputs['no_evens'])

    return all_jobs
