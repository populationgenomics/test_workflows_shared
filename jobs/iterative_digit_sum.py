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
        #!/bin/bash

        # Function to calculate the iterative digit sum
        iterative_digit_sum() {{
        local num=$1
        while [ ${{#num}} -gt 1 ]; do
            local sum=0
            for (( i=0; i<${{#num}}; i++ )); do
            sum=$((sum + ${{num:i:1}}))
            done
            num=$sum
        done
        echo $num
        }}

        # Extract digits from the alphanumeric string and calculate digit sum
        extract_digits_and_sum() {{
        local input_string=$1
        local digits=$(echo "$input_string" | grep -oE '\d')
        local concatenated_digits=$(echo "$digits" | tr -d '\n')

        if [ -z "$concatenated_digits" ]; then
            echo "No digits in input string"
            return
        fi

        # Call the iterative digit sum function
        iterative_digit_sum "$concatenated_digits"
        }}

        # Example usage
        # Replace "$1" with your actual input
        result=$(extract_digits_and_sum {sequencing_group.id})
        echo $result
        echo $result > {job.id_sum}
    """
    job.command(cmd)

    print('-----PRINT ID_SUM-----')
    print(output_file_path)
    b.write_output(job.id_sum, output_file_path)

    return job
