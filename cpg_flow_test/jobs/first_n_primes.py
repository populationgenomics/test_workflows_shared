from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path, config, hail_batch


def first_n_primes_job(
    sequencing_group: SequencingGroup,
    input_file_path: Path,
    job_attrs: dict[str, str],
    output_file_path: Path,
) -> Job:
    b = hail_batch.get_batch()
    job = b.new_job(name=f'First N Primes: {sequencing_group.id}', attributes=job_attrs)
    job.image(config.config_retrieve(['images', 'ubuntu']))
    id_sum_path = b.read_input(input_file_path)

    job.command(f"""
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
    """)

    logger.info('-----PRINT PRIMES-----')
    logger.info(output_file_path)
    b.write_output(job.primes, output_file_path)

    return job
