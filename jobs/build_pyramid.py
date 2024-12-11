from typing import Any

from cpg_flow.targets.sequencing_group import SequencingGroup
from hailtop.batch import Batch
from hailtop.batch.job import Job


def build_pyramid(
    b: Batch,
    sequencing_groups: list[SequencingGroup],
    input_files: dict[str, Any],
    output_file_path: str,
) -> list[Job]:
    title = 'Build A Pyramid'
    # Compute the no evens list for each sequencing group
    sg_jobs = []
    sg_output_files = []
    for sg in sequencing_groups:  # type: ignore
        job = b.new_job(name=title + ': ' + sg.id)
        no_evens_input_file_path = input_files[sg.id]['no_evens']
        no_evens_input_file = b.read_input(no_evens_input_file_path)

        id_sum_input_file_path = input_files[sg.id]['id_sum']
        id_sum_input_file = b.read_input(id_sum_input_file_path)

        pyramid_output_file_path = str(sg.dataset.prefix() / f'{sg.id}_pyramid.txt')
        sg_output_files.append(pyramid_output_file_path)
        cmd = f"""
            pyramid=()
            max_row_size=$(cat {no_evens_input_file} | rev | cut -d' ' -f1 | rev)
            rows=($(cat {no_evens_input_file} | cut -d' ' -f2-))
            # Add header
            pyramid+=("Prime Pyramid for {sg.id}")
            pyramid+=("Generated N: $(cat {id_sum_input_file})")

            for row in "${{rows[@]}}"; do
                total_spaces=$((max_row_size - row))
                left_spaces=$((total_spaces / 2))
                right_spaces=$((total_spaces - left_spaces))
                pyramid+=("$(printf '%*s' $left_spaces)$(printf '%*s' $row | tr ' ' '*')$(printf '%*s' $right_spaces)")
                pyramid+=("$(printf '%*s' $left_spaces)$(printf '%*s' $row | tr ' ' '*')$(printf '%*s' $right_spaces)")
            done

            printf "%s\\n" "${{pyramid[@]}}" > {job.pyramid_file}
        """

        job.command(cmd)
        b.write_output(job.pyramid_file, pyramid_output_file_path)
        sg_jobs.append(job)

    # Merge the no evens lists for all sequencing groups into a single file
    job = b.new_job(name=title)
    job.depends_on(*sg_jobs)
    inputs = ' '.join([b.read_input(f) for f in sg_output_files])
    job.command(f'cat {inputs} >> {job.pyramid}')
    b.write_output(job.pyramid, output_file_path)

    print('-----PRINT PYRAMID-----')
    print(output_file_path)

    return job
