import json

from cpg_flow.stage import CohortStage, DatasetStage, SequencingGroupStage, StageInput, StageOutput, stage
from cpg_flow.targets.cohort import Cohort
from cpg_flow.targets.dataset import Dataset
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


@stage(analysis_keys=['id_sum', 'primes'], analysis_type='prime_pyramid')
class GeneratePrimes(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup) -> dict[str, Path | str]:
        return {
            'id_sum': sequencing_group.dataset.prefix() / f'{sequencing_group.id}_id_sum.txt',
            'primes': sequencing_group.dataset.prefix() / f'{sequencing_group.id}_primes.json',
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


@stage(required_stages=[GeneratePrimes], analysis_keys=['cumulative'], analysis_type='prime_pyramid')
class CumulativeCalc(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup):
        return {
            'cumulative': sequencing_group.dataset.prefix() / f'{sequencing_group.id}_cumulative.json',
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


@stage(required_stages=[CumulativeCalc], analysis_keys=['no_evens'], analysis_type='prime_pyramid')
class FilterEvens(DatasetStage):
    def expected_outputs(self, dataset: Dataset):
        return {
            'no_evens': dataset.prefix() / f'{dataset.name}_no_evens.txt',
        }

    def queue_jobs(self, dataset: Dataset, inputs: StageInput) -> StageOutput | None:
        input_files = inputs.as_dict_by_target(CumulativeCalc)
        b = get_batch()

        no_evens_output_path = str(self.expected_outputs(dataset).get('no_evens', ''))
        job_no_evens = filter_evens(b, dataset.get_sequencing_groups(), input_files, no_evens_output_path)

        jobs = [job_no_evens]

        return self.make_outputs(
            dataset,
            data=self.expected_outputs(dataset),
            jobs=jobs,
        )


@stage(required_stages=[GeneratePrimes, FilterEvens], analysis_keys=['pyramid'], analysis_type='prime_pyramid')
class BuildAPrimePyramid(CohortStage):
    def expected_outputs(self, cohort: Cohort):
        return {
            'pyramid': cohort.prefix() / f'{cohort.name}_pyramid.txt',
        }

    def queue_jobs(self, cohort: Cohort, inputs: StageInput) -> StageOutput | None:
        input_files = inputs.as_dict_by_target(FilterEvens)
        b = get_batch()

        no_evens_output_path = str(self.expected_outputs(cohort).get('no_evens', ''))
        job_no_evens = build_pyramid(b, cohort.get_sequencing_groups(), input_files, no_evens_output_path)

        jobs = [job_no_evens]

        return self.make_outputs(
            cohort,
            data=self.expected_outputs(cohort),
            jobs=jobs,
        )
