from typing import Any

from loguru import logger

from hailtop.batch.job import Job

from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_flow.utils import dependency_handler
from cpg_utils import Path, config, hail_batch


def build_pyramid_job(
    sequencing_groups: list[SequencingGroup],
    input_files: dict[str, Any],
    job_attrs: dict[str, str],
    output_file_path: Path,
) -> list[Job]:
    b = hail_batch.get_batch()

    title = 'Build A Pyramid'
    # Compute the no evens list for each sequencing group
    all_jobs: list[Job] = []
    sg_output_files: list[Path] = []
    for sg in sequencing_groups:
        job = b.new_bash_job(name=title + ': ' + sg.id, attributes=job_attrs | {'sequencing_group': sg.id})
        job.image(config.config_retrieve(['images', 'ubuntu']))

        no_evens_input_file = b.read_input(input_files[sg.id]['no_evens'])

        id_sum_input_file = b.read_input(input_files[sg.id]['id_sum'])

        pyramid_output_file_path = sg.dataset.prefix() / f'{sg.id}_pyramid.txt'
        sg_output_files.append(pyramid_output_file_path)
        job.command(f"""
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
        """)

        b.write_output(job.pyramid_file, pyramid_output_file_path)
        all_jobs.append(job)

    # Merge the no evens lists for all sequencing groups into a single file
    job = b.new_bash_job(name=title, attributes=job_attrs | {'tool': 'cat'})
    job.image(config.config_retrieve(['images', 'ubuntu']))

    # set and extend dependency list
    dependency_handler(job, all_jobs, append_to_tail=True)

    inputs = ' '.join([b.read_input(f) for f in sg_output_files])
    job.command(f'cat {inputs} >> {job.pyramid}')
    b.write_output(job.pyramid, output_file_path)

    logger.info('-----PRINT PYRAMID-----')
    logger.info(output_file_path)

    return all_jobs
