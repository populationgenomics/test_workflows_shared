from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job
from hailtop.batch.resource import ResourceFile


def filter_evens(
    b: Batch,
    sequencing_group: SequencingGroup,
    input_file_path: str,
    output_file: ResourceFile,
    job_wait_for: Job | None = None,
) -> list[Job]:
    title = 'Filter Evens'
    job = b.new_job(name=title)
    cumulative_path = b.read_input(input_file_path)

    if job_wait_for:
        job.depends_on(job_wait_for)

    cmd = f"""
    numbers=($(cat {cumulative_path}))
    result=()
    for num in "${{numbers[@]}}"; do
        if (( num % 2 != 0 )); then
            result+=("$num")
        fi
    done
    echo "{sequencing_group.id}: ${{result[@]}}" >> {output_file}
    """

    job.command(cmd)
    return job
