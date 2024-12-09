from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job


def filter_evens(
    b: Batch,
    input_file_path: str,
    output_file_path: str,
) -> list[Job]:
    title = 'Filter Evens'
    job = b.new_job(name=title)
    cumulative_path = b.read_input(input_file_path)

    cmd = f"""
    numbers=($(cat {cumulative_path}))
    result=()
    for num in "${{numbers[@]}}"; do
        if (( num % 2 != 0 )); then
            result+=("$num")
        fi
    done
    echo "${{result[@]}}" > {job.no_evens}
    """

    job.command(cmd)

    print('-----PRINT NO EVENS-----')
    print(output_file_path)
    b.write_output(job.no_evens, output_file_path)

    return job
