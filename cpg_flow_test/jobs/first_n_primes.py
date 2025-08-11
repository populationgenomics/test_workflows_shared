from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job
from loguru import logger


def first_n_primes(
    b: Batch,
    sequencing_group: SequencingGroup,
    input_file_path: str,
    job_attrs: dict[str, str],
    output_file_path: str,
    depends_on: Job,
) -> list[Job]:
    title = f'First N Primes: {sequencing_group.id}'
    job = b.new_job(name=title, attributes=job_attrs)
    id_sum_path = b.read_input(input_file_path)

    if depends_on:
        job.depends_on(depends_on)

    cmd = f"""
    is_prime() {{
        local num=$1
        if [ $num -lt 2 ]; then
            echo 0
            return
        fi
        for ((i=2; i*i<=$num; i++)); do
            if [ $(($num % $i)) -eq 0 ]; then
                echo 0
                return
            fi
        done
        echo 1
    }}

    n=$(cat {id_sum_path})  # Replace with the desired number of primes
    primes=()
    candidate=2
    while [ ${{#primes[@]}} -lt $n ]; do
        if [ $(is_prime $candidate) -eq 1 ]; then
            primes+=($candidate)
        fi
        candidate=$((candidate + 1))
    done

    echo ${{primes[@]}} > {job.primes}
    """

    job.command(cmd)

    logger.info('-----PRINT PRIMES-----')
    logger.info(output_file_path)
    b.write_output(job.primes, output_file_path)

    return job
