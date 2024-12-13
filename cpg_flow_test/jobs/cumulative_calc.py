from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job


def cumulative_calc(
    b: Batch,
    input_file_path: str,
    output_file_path: str,
) -> list[Job]:
    title = 'Cumulative Calc'
    job = b.new_job(name=title)
    primes_path = b.read_input(input_file_path)

    cmd = f"""
    primes=($(cat {primes_path}))
    csum=0
    cumulative=()
    for prime in "${{primes[@]}}"; do
        ((csum += prime))
        cumulative+=("$csum")
    done
    echo "${{cumulative[@]}}" > {job.cumulative}
    """

    job.command(cmd)

    print('-----PRINT CUMULATIVE-----')
    print(output_file_path)
    b.write_output(job.cumulative, output_file_path)

    return job
