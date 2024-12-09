from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job


def first_n_primes(
    b: Batch,
    input_file_path: str,
    output_file_path: str,
) -> list[Job]:
    title = 'First N Primes'
    job = b.new_job(name=title)

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

    n=$(cat {input_file_path})  # Replace with the desired number of primes
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

    print('-----PRINT PRIMES-----')
    print(output_file_path)
    b.write_output(job.primes, output_file_path)

    return job
