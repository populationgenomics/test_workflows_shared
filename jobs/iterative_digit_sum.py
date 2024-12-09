from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job


def iterative_digit_sum(
    b: Batch,
    sequencing_group: SequencingGroup,
    output_file_path: str,
) -> list[Job]:
    title = 'Iterative Digit Sum'
    job = b.new_job(name=title)

    cmd = f"""\
    # Extract digits from the string
    digits=$(echo {sequencing_group.id} | grep -o '[0-9]' | paste -sd+ - | bc)
    # Calculate the sum iteratively
    n=$digits
    while [ $n -ge 10 ]; do
        n=$(echo $n | grep -o '[0-9]' | paste -sd+ - | bc)
    done
    echo $n > {job.id_sum}
    """
    job.command(cmd)

    print('-----PRINT ID_SUM-----')
    print(output_file_path)
    b.write_output(job.id_sum, output_file_path)

    return job
