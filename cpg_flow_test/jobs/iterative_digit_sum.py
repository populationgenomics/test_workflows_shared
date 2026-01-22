from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path, hail_batch


def iterative_digit_sum_job(
    sequencing_group: SequencingGroup,
    job_attrs: dict[str, str],
    output_file_path: Path,
) -> Job:
    b = hail_batch.get_batch()
    job = b.new_job(name=f'Iterative Digit Sum: {sequencing_group.id}', attributes=job_attrs)

    job.command(f"""\
        #!/bin/bash

        # Function to calculate the iterative digit sum
        iterative_digit_sum() {{
            local num=$1
            while [ ${{#num}} -gt 2 ]; do
                local sum=0
                for (( i=0; i<${{#num}}; i++ )); do
                sum=$((sum + ${{num:i:1}}))
                done
                num=$sum
            done
            num=$((num / 2))  # Divide by two
            echo $num
        }}

        # Extract digits from the alphanumeric string and calculate digit sum
        extract_digits_and_sum() {{
        local input_string=$1
        local digits=$(echo "$input_string" | grep -oE '[0-9]+')
        local concatenated_digits=$(echo "$digits" | tr -d '\n')

        if [ -z "$concatenated_digits" ]; then
            echo "No digits in input string"  >&2  # Redirect to stderr
            return
        fi

        # Call the iterative digit sum function
        iterative_digit_sum "$concatenated_digits"
        }}

        echo "Input: {sequencing_group.id}\n"
        result=$(extract_digits_and_sum {sequencing_group.id})
        echo "Result: $result\n"
        echo $result > {job.id_sum}
    """)

    logger.info('-----PRINT ID_SUM-----')
    logger.info(output_file_path)
    b.write_output(job.id_sum, output_file_path)

    return job
