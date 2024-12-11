import json

from cpg_flow.stage import CohortStage, MultiCohortStage, SequencingGroupStage, StageInput, StageOutput, stage
from cpg_flow.targets.cohort import Cohort
from cpg_flow.targets.multicohort import MultiCohort
from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path
from cpg_utils.hail_batch import get_batch

from jobs import build_pyramid, cumulative_calc, filter_evens, first_n_primes, iterative_digit_sum

"""
Here's a fun programming task with four interdependent steps, using the concept of **prime numbers** and their relationships:

---

### Task: Prime Pyramid
Write a program that builds a "Prime Pyramid" based on a given input number \( N \). The pyramid is built in four steps:

#### Step 1: **Generate Prime Numbers**
Write a function to generate the first \( N \) prime numbers. For example, if \( N = 5 \), the output would be `[2, 3, 5, 7, 11]`.

#### Step 2: **Calculate Cumulative Sums**
Using the prime numbers generated in Step 1, calculate a list of cumulative sums. Each cumulative sum is the sum of the primes up to that index.
Example: For `[2, 3, 5, 7, 11]`, the cumulative sums are `[2, 5, 10, 17, 28]`.

#### Step 3: **Filter Even Numbers**
From the cumulative sums generated in Step 2, filter out the even numbers.
Example: For `[2, 5, 10, 17, 28]`, the result is `[5, 17]`.

#### Step 4: **Build the Prime Pyramid**
Using the filtered numbers from Step 3, construct a pyramid. Each level of the pyramid corresponds to a filtered number, and the number determines how many stars `*` appear on that level.
Example: For `[5, 17]`, the pyramid is:
```
*****
*****************
```

---

### Optional Extensions:
1. Allow the user to input \( N \) dynamically.
2. Visualize the pyramid with formatting, like centering the stars.
3. Add validation to ensure \( N \) is a positive integer.
4. Include unit tests for each step.

This task is simple, yet it combines loops, conditionals, and basic data manipulations in a creative way!
"""

WORKFLOW_FOLDER = 'prime_pyramid'


@stage(analysis_keys=['id_sum', 'primes'], analysis_type='custom')
class GeneratePrimes(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup) -> dict[str, Path | str]:
        return {
            'id_sum': sequencing_group.dataset.prefix() / WORKFLOW_FOLDER / f'{sequencing_group.id}_id_sum.txt',
            'primes': sequencing_group.dataset.prefix() / WORKFLOW_FOLDER / f'{sequencing_group.id}_primes.json',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        # Get batch
        b = get_batch()

        # Write id_sum to output file
        id_sum_output_path = str(self.expected_outputs(sequencing_group).get('id_sum', ''))
        job_id_sum = iterative_digit_sum(b, sequencing_group, id_sum_output_path)

        # Generate first N primes
        primes_output_path = str(self.expected_outputs(sequencing_group).get('primes', ''))
        job_primes = first_n_primes(b, id_sum_output_path, primes_output_path)

        jobs = [job_id_sum, job_primes]

        return self.make_outputs(sequencing_group, data=self.expected_outputs(sequencing_group), jobs=jobs)  # type: ignore


@stage(required_stages=[GeneratePrimes], analysis_keys=['cumulative'], analysis_type='custom')
class CumulativeCalc(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup):
        return {
            'cumulative': sequencing_group.dataset.prefix()
            / WORKFLOW_FOLDER
            / f'{sequencing_group.id}_cumulative.json',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        input_json = inputs.as_path(sequencing_group, GeneratePrimes, 'primes')
        b = get_batch()

        cumulative_calc_output_path = str(self.expected_outputs(sequencing_group).get('cumulative', ''))
        job_cumulative_calc = cumulative_calc(b, input_json, cumulative_calc_output_path)

        jobs = [job_cumulative_calc]

        return self.make_outputs(
            sequencing_group,
            data=self.expected_outputs(sequencing_group),
            jobs=jobs,
        )


@stage(required_stages=[CumulativeCalc], analysis_keys=['no_evens'], analysis_type='custom')
class FilterEvens(CohortStage):
    def expected_outputs(self, cohort: Cohort):
        sg_outputs = {
            k: str(sg.dataset.prefix() / f'{sg.id}_no_evens.txt') for k, sg in cohort.get_sequencing_groups().items()
        }
        sg_outputs['no_evens'] = cohort.analysis_dataset.prefix() / WORKFLOW_FOLDER / f'{cohort.name}_no_evens.txt'
        return sg_outputs

    def queue_jobs(self, cohort: Cohort, inputs: StageInput) -> StageOutput | None:
        input_files = inputs.as_dict_by_target(CumulativeCalc)
        b = get_batch()

        sg_outputs = self.expected_outputs(cohort)
        no_evens_output_path = sg_outputs['no_evens']
        job_no_evens = filter_evens(b, cohort.get_sequencing_groups(), input_files, sg_outputs, no_evens_output_path)

        jobs = [job_no_evens]

        return self.make_outputs(
            cohort,
            data=self.expected_outputs(cohort),
            jobs=jobs,
        )


@stage(required_stages=[GeneratePrimes, FilterEvens], analysis_keys=['pyramid'], analysis_type='custom')
class BuildAPrimePyramid(MultiCohortStage):
    def expected_outputs(self, multicohort: MultiCohort):
        return {
            'pyramid': multicohort.analysis_dataset.prefix() / WORKFLOW_FOLDER / f'{multicohort.name}_pyramid.txt',
        }

    def queue_jobs(self, multicohort: MultiCohort, inputs: StageInput) -> StageOutput | None:
        input_files_filter_evens = inputs.as_dict_by_target(FilterEvens)
        input_files_generate_primes = inputs.as_dict_by_target(GeneratePrimes)
        print('----INPUT FILES FILTER EVENS----')
        print(input_files_filter_evens)
        print('----INPUT FILES GENERATE PRIMES----')
        print(input_files_generate_primes)

        input_files = {k: {**v, **input_files_generate_primes[k]} for k, v in input_files_filter_evens.items()}

        print('----INPUT FILES----')
        print(input_files)

        b = get_batch()

        pyramid_output_path = str(self.expected_outputs(multicohort).get('pyramid', ''))
        job_pyramid = build_pyramid(b, multicohort.get_sequencing_groups(), input_files, pyramid_output_path)

        jobs = [job_pyramid]

        return self.make_outputs(
            multicohort,
            data=self.expected_outputs(multicohort),
            jobs=jobs,
        )
