from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils.config import config_retrieve
from cpg_utils.hail_batch import get_batch


def iterative_digit_sum_job(
    sequencing_group: SequencingGroup,
    job_attrs: dict[str, str],
    output_file_path: str,
) -> list[Job]:
    b = get_batch()
    title = f'Iterative Digit Sum: {sequencing_group.id}'
    job = b.new_job(name=title, attributes=job_attrs)
    job.image(config_retrieve(['workflow', 'driver_image']))

    cmd = f"""\
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
    """
    job.command(cmd)

    logger.info('-----PRINT ID_SUM-----')
    logger.info(output_file_path)
    b.write_output(job.id_sum, output_file_path)

    return job
