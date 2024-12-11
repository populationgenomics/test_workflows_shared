from typing import Any

from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job
from hailtop.batch.resource import ResourceFile


def build_pyramid(
    b: Batch,
    sequencing_groups: list[SequencingGroup],
    input_files: dict[str, Any],
    output_file_path: ResourceFile,
) -> list[Job]:
    title = 'Filter Evens'
    job = b.new_job(name=title)

    # Compute the no evens list for each sequencing group
    sg_output_files = []
    for sg in sequencing_groups:  # type: ignore
        input_file_path = input_files[sg.id]['cumulative']
        no_evens_input_file = b.read_input(input_file_path)
        no_evens_output_file_path = sg.dataset.prefix() / f'{sg.id}_no_evens.txt'
        sg_output_files.append(no_evens_output_file_path)

        cmd = ''

        # cmd = f"""
        #     pyramid=()
        #     max_row_size={{rows[-1]}}

        #     # Add header
        #     pyramid+=("Prime Pyramid for {{sequencing_group.id}}")
        #     pyramid+=("Generated N: {n}")

        #     for row in {rows[@]}; do
        #         total_spaces=$((max_row_size - row))
        #         left_spaces=$((total_spaces / 2))
        #         right_spaces=$((total_spaces - left_spaces))
        #         pyramid+=("$(printf '%*s' $left_spaces)$(printf '%*s' $row | tr ' ' '*')$(printf '%*s' $right_spaces)")
        #     done

        #     printf "%s\\n" "${pyramid[@]}" > {job.pyramid_file}
        # """

        job.command(cmd)
        b.write_output(job.no_evens_sg_file, no_evens_output_file_path)

    # Merge the no evens lists for all sequencing groups into a single file
    inputs = ' '.join([b.read_input(f) for f in sg_output_files])
    job.command(f'cat {inputs} >> {job.no_evens_file}')

    print('-----PRINT NO EVENS-----')
    print(output_file_path)
    b.write_output(job.no_evens_file, output_file_path)

    return job
