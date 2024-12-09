import json

from cpg_flow.stage import CohortStage, DatasetStage, SequencingGroupStage, StageInput, StageOutput, stage
from cpg_flow.targets.sequencing_group import SequencingGroup
from cpg_utils import Path
from cpg_utils.hail_batch import get_batch

from jobs import first_n_primes, iterative_digit_sum

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


@stage
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


@stage(
    required_stages=[GeneratePrimes],
)
class CumulativeCalc(SequencingGroupStage):
    def expected_outputs(self, sequencing_group: SequencingGroup):
        return {
            'cumulative': sequencing_group.dataset.prefix() / f'{sequencing_group.id}_cumulative.json',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        input_json = inputs.as_path(sequencing_group, GeneratePrimes, 'primes')
        print('-----PRINT INPUT JSON-----')
        print(input_json)
        b = get_batch()

        j = b.new_python_job(name='cumulative-calc')
        # j.call(load_primes_json, str(input_json))

        # Write cumulative sums to output file
        # j.command(f"echo '{json.dumps(cumulative)}' > {j.cumulative}")
        # b.write_output(primes.as_json(), str(self.expected_outputs(sequencing_group).get('cumulative', '')))

        return self.make_outputs(
            sequencing_group,
            data=self.expected_outputs(sequencing_group).get('cumulative'),
            jobs=[j],
        )

    def cumulative_sum(self, primes: list[int]) -> list[int]:
        csum = 0
        cumulative = []
        for i in range(len(primes)):
            csum += primes[i]
            cumulative.append(csum)

        return cumulative


@stage(required_stages=[CumulativeCalc])
class FilterEvens(DatasetStage):
    def expected_outputs(self, sequencing_group: SequencingGroup):
        return {
            'no_evens': sequencing_group.dataset.prefix() / f'{sequencing_group.id}_no_evens.json',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        input_json = inputs.as_path(sequencing_group, CumulativeCalc, 'cumulative')
        cumulative_primes = json.load(open(input_json))

        no_evens = self.filter_evens(cumulative_primes)

        b = get_batch()
        j = b.new_job(name='filter-evens')

        # Write cumulative sums to output file
        j.command(f"echo '{json.dumps(no_evens)}' > {j.no_evens}")
        b.write_output(j.cumulative, str(self.expected_outputs(sequencing_group).get('no_evens', '')))

        return self.make_outputs(
            sequencing_group,
            data=self.expected_outputs(sequencing_group).get('no_evens'),
            jobs=[j],
        )

    def filter_evens(self, numbers: list[int]) -> list[int]:
        return [num for num in numbers if num % 2 != 0]


@stage(
    required_stages=[GeneratePrimes, FilterEvens],
)
class BuildAPrimePyramid(CohortStage):
    def expected_outputs(self, sequencing_group: SequencingGroup):
        return {
            'pyramid': sequencing_group.dataset.prefix() / f'{sequencing_group.id}_pyramid.txt',
        }

    def queue_jobs(self, sequencing_group: SequencingGroup, inputs: StageInput) -> StageOutput | None:
        input_json = inputs.as_path(sequencing_group, FilterEvens, 'no_evens')
        row_sizes = json.load(open(input_json))

        input_n = inputs.as_path(sequencing_group, GeneratePrimes, 'id_sum')
        n = int(open(input_n).read().strip())

        pyramid = self.file_contents(sequencing_group, n, row_sizes)

        b = get_batch()
        j = b.new_job(name='filter-evens')

        # Write pyramid to output file
        j.command(f"echo '{json.dumps(pyramid)}' > {j.pyramid}")
        b.write_output(j.cumulative, str(self.expected_outputs(sequencing_group).get('pyramid', '')))

        return self.make_outputs(
            sequencing_group,
            data=self.expected_outputs(sequencing_group).get('pyramid'),
            jobs=[j],
        )

    def file_contents(self, sequencing_group: SequencingGroup, n: int, rows: list[int]) -> str:
        pyramid = []
        max_row_size = rows[-1]

        # Add header
        pyramid.append(f'Prime Pyramid for {sequencing_group.id}')
        pyramid.append(f'Generated N: {n}')

        for row in rows:
            total_spaces = max_row_size - row
            left_spaces = total_spaces // 2
            right_spaces = total_spaces - left_spaces
            pyramid.append(' ' * left_spaces + '*' * row + ' ' * right_spaces)

        return '\n'.join(pyramid)
