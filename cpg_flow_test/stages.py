from typing import Any

from jobs import build_pyramid, cumulative_calc, filter_evens, first_n_primes, iterative_digit_sum, say_hi
from loguru import logger

from cpg_flow.stage import CohortStage, MultiCohortStage, SequencingGroupStage, StageInput, StageOutput, stage
from cpg_flow.targets.cohort import Cohort
from cpg_flow.targets.multicohort import MultiCohort
from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path

"""
Here's a fun programming task with four steps, using the concept of **prime numbers** and their relationships:

---

### Task: Prime Pyramid
Write a program that builds a "Prime Pyramid" based on a given input number \( N \). The pyramid is built in four steps:

#### Step 1: **Generate Prime Numbers**
Write a function to generate the first `N` prime numbers. i.e. if `N=5``, the output would be `[2, 3, 5, 7, 11]`.

#### Step 2: **Calculate Cumulative Sums**
Using the prime numbers generated in Step 1, calculate a list of cumulative sums.
Each cumulative sum is the sum of the primes up to that index.
Example: For `[2, 3, 5, 7, 11]`, the cumulative sums are `[2, 5, 10, 17, 28]`.

#### Step 3: **Filter Even Numbers**
From the cumulative sums generated in Step 2, filter out the even numbers.
Example: For `[2, 5, 10, 17, 28]`, the result is `[5, 17]`.

#### Step 4: **Build the Prime Pyramid**
Using the filtered numbers from Step 3, construct a pyramid.
Each pyramid level corresponds to a filtered number, and the number determines how many stars `*` appear on that level.
Example: For `[5, 17]`, the pyramid is:
```
*****
*****************
```

---

### Optional Extensions:
1. Allow the user to input `N`` dynamically.
2. Visualize the pyramid with formatting, like centering the stars.
3. Add validation to ensure `N` is a positive integer.
4. Include unit tests for each step.

This task is simple, yet it combines loops, conditionals, and basic data manipulations in a creative way!
"""

WORKFLOW_FOLDER = 'prime_pyramid'


@stage(analysis_keys=['id_sum', 'primes'], analysis_type='custom')
class GeneratePrimes(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup) -> dict[str, Path]:
        return {
            'id_sum': sequencing_group.dataset.prefix() / WORKFLOW_FOLDER / f'{sequencing_group.id}_id_sum.txt',
            'primes': sequencing_group.dataset.prefix() / WORKFLOW_FOLDER / f'{sequencing_group.id}_primes.txt',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput:
        # Print out alignment input for this sequencing group
        logger.info('-----ALIGNMENT INPUT-----')
        logger.info(sequencing_group.alignment_input)

        outputs = self.expected_outputs(sequencing_group)

        # Write id_sum to output file
        job_id_sum = iterative_digit_sum.iterative_digit_sum_job(
            sequencing_group,
            self.get_job_attrs(sequencing_group),
            outputs['id_sum'],
        )

        # Generate first N primes
        primes_output_path = str(self.expected_outputs(sequencing_group).get('primes', ''))
        job_primes = first_n_primes.first_n_primes_job(
            sequencing_group,
            outputs['id_sum'],
            self.get_job_attrs(sequencing_group),
            outputs['primes'],
        )
        # set a dependency
        job_primes.depends_on(job_id_sum)

        jobs = [job_id_sum, job_primes]

        return self.make_outputs(sequencing_group, data=outputs, jobs=jobs)


@stage(required_stages=[GeneratePrimes], analysis_keys=['cumulative'], analysis_type='custom')
class CumulativeCalc(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup) -> dict[str, Path]:
        return {
            'cumulative': sequencing_group.dataset.prefix() / WORKFLOW_FOLDER / f'{sequencing_group.id}_cumulative.txt',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        input_txt = inputs.as_path(sequencing_group, GeneratePrimes, 'primes')
        outputs = self.expected_outputs(sequencing_group)

        job_cumulative_calc = cumulative_calc.cumulative_calc_job(
            sequencing_group,
            input_txt,
            self.get_job_attrs(sequencing_group),
            outputs['cumulative'],
        )

        return self.make_outputs(
            sequencing_group,
            data=outputs,
            jobs=job_cumulative_calc,
        )


@stage(required_stages=[GeneratePrimes], analysis_keys=['hello'], analysis_type='custom')
class SayHi(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup) -> dict[str, Path]:
        return {
            'hello': sequencing_group.dataset.prefix() / WORKFLOW_FOLDER / f'{sequencing_group.id}_cumulative.txt',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        outputs = self.expected_outputs(sequencing_group)
        return self.make_outputs(
            sequencing_group,
            data=outputs,
            jobs=say_hi.say_hi_job(sequencing_group, self.get_job_attrs(sequencing_group), outputs['hello']),
        )


@stage(required_stages=[CumulativeCalc], analysis_keys=['no_evens'], analysis_type='custom')
class FilterEvens(CohortStage):
    def expected_outputs(self, cohort: Cohort) -> dict[str, Path]:
        sg_outputs = {
            sg.id: sg.dataset.prefix() / WORKFLOW_FOLDER / f'{sg.id}_no_evens.txt'
            for sg in cohort.get_sequencing_groups()
        }
        sg_outputs['no_evens'] = cohort.dataset.prefix() / WORKFLOW_FOLDER / f'{cohort.name}_no_evens.txt'
        return sg_outputs

    def queue_jobs(self, cohort: Cohort, inputs: StageInput) -> StageOutput | None:
        input_files = inputs.as_dict_by_target(CumulativeCalc)
        outputs = self.expected_outputs(cohort)

        job_no_evens = filter_evens.filter_evens_job(
            cohort.get_sequencing_groups(),
            input_files,
            self.get_job_attrs(cohort),
            outputs,
        )

        return self.make_outputs(
            cohort,
            data=outputs,
            jobs=job_no_evens,
        )


@stage(required_stages=[GeneratePrimes, FilterEvens], analysis_keys=['pyramid'], analysis_type='custom')
class BuildAPrimePyramid(MultiCohortStage):
    def expected_outputs(self, multicohort: MultiCohort) -> dict[str, Path]:
        return {
            'pyramid': multicohort.analysis_dataset.prefix() / WORKFLOW_FOLDER / f'{multicohort.name}_pyramid.txt',
        }

    def queue_jobs(self, multicohort: MultiCohort, inputs: StageInput) -> StageOutput | None:
        input_files_filter_evens = inputs.as_dict_by_target(FilterEvens)
        logger.info('----INPUT FILES FILTER EVENS----')
        logger.info(input_files_filter_evens)

        input_files_generate_primes = inputs.as_dict_by_target(GeneratePrimes)
        logger.info('----INPUT FILES GENERATE PRIMES----')
        logger.info(input_files_generate_primes)

        outputs = self.expected_outputs(multicohort)

        input_files: dict[str, dict[str, Any]] = {}
        for cohort in multicohort.get_cohorts():
            for sg in cohort.get_sequencing_groups():
                input_files[sg.id] = {
                    'no_evens': input_files_filter_evens[cohort.id][sg.id],
                    'id_sum': input_files_generate_primes[sg.id]['id_sum'],
                    'primes': input_files_generate_primes[sg.id]['primes'],
                }

        logger.info('----INPUT FILES----')
        logger.info(input_files)

        job_pyramid = build_pyramid.build_pyramid_job(
            multicohort.get_sequencing_groups(),
            input_files,
            self.get_job_attrs(multicohort),
            outputs['pyramid'],
        )

        return self.make_outputs(
            multicohort,
            data=outputs,
            jobs=job_pyramid,
        )
