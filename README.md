
<h1 align="center">
  <br>
  <a href="http://www.amitmerchant.com/electron-markdownify"><img src="./assets/tws.jpg" alt="Markdownify" width="200"></a>
  <br>
  Test Workflows Shared
  <br>
</h1>

<h4 align="center">A template test workflows repository that works with <a href="https://github.com/populationgenomics/cpg-flow" target="_blank">CPG Flow</a></h4>

<p align="center">
  <a href="https://img.shields.io/github/actions/workflow/status/populationgenomics/test_workflows_shared/security.yaml?style=for-the-badge&label=pip-audit">
    <img alt="GitHub Actions Workflow Status" src="https://img.shields.io/github/actions/workflow/status/populationgenomics/test_workflows_shared/security.yaml?style=for-the-badge&label=pip-audit">
  </a>
  <a href="https://img.shields.io/github/license/populationgenomics/test_workflows_shared?style=for-the-badge
  "><img alt="GitHub License" src="https://img.shields.io/github/license/populationgenomics/test_workflows_shared?style=for-the-badge">
</a>
  <a href="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fpopulationgenomics%2Ftest_workflows_shared%2Fmain%2Fpyproject.toml&style=for-the-badge
  ">
      <img alt="Python Version from PEP 621 TOML" src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fpopulationgenomics%2Ftest_workflows_shared%2Fmain%2Fpyproject.toml&style=for-the-badge">

  </a>
</p>

<p align="center">
  <a href="#background">Background</a> •
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#editing-in-an-ide">Editing in an IDE</a> •
  <a href="#related">Related</a> •
  <a href="#license">License</a>
</p>

## Background

The tests_workflows_shared repository serves as a dedicated testing space for both cpg_flow and pipeline developers. It is designed to facilitate manual, integrated end-to-end (E2E) validation of the cpg_flow package, ensuring its robustness and reliability in production-like environments. By interfacing with Metamist and leveraging a cohort from the fewgenomes project, the repository enables  testing of new builds and modifications before deployment.

For pipeline developers who are new to cpg_flow, this repository provides a practical trial workflow, offering a hands-on introduction to its core functionalities and best practices. This dual-purpose approach not only supports continuous improvement of cpg_flow but also accelerates onboarding and skill development for new contributors.

Beyond its primary focus on testing, the repository promotes standardization through:

- Enforcement of consistent naming conventions aligned with CPG standards.
- Automated package and dependency updates using Renovate.
- Dependency management facilitated by setuptools and pip-tools.

By combining rigorous testing capabilities with a standardised development framework, tests_workflows_shared ensures high-quality pipeline development and fosters a cohesive developer experience.

## Key Features

* Uses `pyproject.toml` to manage dependencies
* Uses `renovate` for package upgrades
* Uses `analysis-runner` to run the test workflow
* The `jobs` and `stages` are defined in separate files:
  * The `cpg_flow_test/jobs/` directory contains the job definitions that can be reused across stages.
  * The `cpg_flow_test/stages.py` file contains the stage definitions, which call the jobs.
* The `cpg_flow_test/workflow.py` file contains the test workflow definition.

## How To Use

From your command line:

```bash
# Clone this repository
$ git clone https://github.com/populationgenomics/test_workflows_shared

# Go into the repository
$ cd test_workflows_shared

# Go to the test folder
$ cd cpg_flow_test

# Run the test with the bash script
$ chmod +x run-test-workflow.sh

# See the notes below on how to find a valid path/tag.
# The default path is australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:0.1.0-alpha.14
$ ./run-test-workflow.sh --image "australia-southeast1-docker.pkg.dev/cpg-common/images/cpg_flow:<tag_id>"


```

If the job is successfully created, the analysis-runner output will include a job URL. This driver job will trigger additional jobs, which can be monitored via the /batches page on Hail. Monitoring these jobs helps verify that the workflow ran successfully. When all expected jobs complete without errors, this confirms the successful execution of the test workflow and indicates that the cpg_flow package is functioning as intended.

### Notes

- You will need to have `analysis-runner` installed in your environment. See the [analysis-runner](https://github.com/populationgenomics/analysis-runner) for more information or install it with `pipx install analysis-runner`.

- **Testing with Different Image Tags**: Running the pipeline on different tags of the cpg_flow image is valuable for validating unmerged functionality in the cpg_flow repository. To ensure stability, you can default to a recent release tag when testing with a stable version of the cpg_flow image.

- **Finding a Valid Tag**: A valid tag can be obtained from the most recent [cpg-flow](https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml)[Docker workflow](https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml) runs. Look under the print docker tag job of the workflow. Be mindful of the distinction between images (stable) and images-tmp (test images pruned fortnightly).


## Editing in an IDE

To enable syntax highlighting in your IDE, you will need to install dependencies.

```bash
# Create a virtual environment - method of your choice - and source in
# make sure the version of python available in your virtualenv satisfyies the
# requirement in the pyproject.toml requires-python attribute
$ source .venv/bin/activate

# Then install the dev and/or main dependencies as shown
$ pip install -r requirements.txt
$ pip install -r requirements-dev.txt

# Running the following make commands does the same
$ make install      # pip install -r requirements.txt
$ make install-dev  # pip install -r requirements-dev.txt
$ make install0all  # ^run both of the above

# To compile dependencies run
$ make compile
```

## Related

[cpg-flow](https://github.com/populationgenomics/cpg-flow) - supports various stages of genomic data processing, from raw data ingestion to final analysis outputs, making it easier for researchers to manage and scale their population genomics workflows.

## License

[MIT](LICENSE)
