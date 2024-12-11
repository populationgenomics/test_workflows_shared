from typing import Any

from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job
from hailtop.batch.resource import ResourceFile


def filter_evens(
    b: Batch,
    sequencing_groups: list[SequencingGroup],
    input_files: dict[str, Any],
    output_file_path: ResourceFile,
) -> list[Job]:
    title = 'Filter Evens'

    # Compute the no evens list for each sequencing group
    sg_jobs = []
    sg_output_files = []
    for sg in sequencing_groups:  # type: ignore
        job = b.new_job(name=title + ': ' + sg.id)
        input_file_path = input_files[sg.id]['cumulative']
        no_evens_input_file = b.read_input(input_file_path)
        no_evens_output_file_path = str(sg.dataset.prefix() / f'{sg.id}_no_evens.txt')
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
    job = b.new_job(name=title)
    job.depends_on(sg_jobs)
    inputs = ' '.join([b.read_input(f) for f in sg_output_files])
    job.command(f'cat {inputs} >> {job.no_evens_file}')
    b.write_output(job.no_evens_file, output_file_path)

    print('-----PRINT NO EVENS-----')
    print(output_file_path)

    return job
