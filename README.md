
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
  <a href="#key-features">Key Features</a> •
  <a href="#how-to-use">How To Use</a> •
  <a href="#editing-in-an-ide">Editing in an IDE</a> •
  <a href="#related">Related</a> •
  <a href="#license">License</a>
</p>


## Key Features

* Uses `uv` to manage dependencies
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

# See the notes below on how to find a valid tag.
# The default tag is cpg_flow:0.x.x
$ ./run-test-workflow.sh --image-tag "cpg_flow:<tag_id>"
```


> **Notes**
>
> * You will need to have `analysis-runner` installed in your environment. See the [analysis-runner](https://github.com/populationgenomics/analysis-runner) for more information or install it with `pipx install analysis-runner`.
> * You will need a valid tag above, which you can find from the most recent [`cpg-flow` docker workflow](https://github.com/populationgenomics/cpg-flow/actions/workflows/docker.yaml) runs, under the `print docker tag` job of the workflow.


You should receive a job url from the `analysis-runner` output, if the job was created successfully. This job should spin up additional jobs that can be found from the `/batches` page on Hail.

## Editing in an IDE

To enable syntax highlighting in your IDE, you will need to install dependencies.

```bash
# Install dependencies
# `uv` documentation: https://docs.astral.sh/uv/
$ uv sync

# Activate the virtual environment
$ source .venv/bin/activate
```

## Related

[cpg-flow](https://github.com/populationgenomics/cpg-flow) - supports various stages of genomic data processing, from raw data ingestion to final analysis outputs, making it easier for researchers to manage and scale their population genomics workflows.

## License

[MIT](LICENSE)
