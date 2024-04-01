# Evaluation using software repositories from CESSDA and FAIR-EASE

For milestone 5.6, we tested the extension using lists of software repositories kindly provided by [CESSDA](https://www.cessda.eu/) and [FAIR-EASE](https://fairease.eu/).

The CESSDA repositories were evaluated against the CESSDA-specific metric tests, whereas the FAIR-EASE repositories were evaluated against the generic metric tests. The results are presented in the milestone report linked from the main README of this repository.

The contents of this folder are as follows:
- [`cessda_repos.txt`](./cessda_repos.txt) and [`fair_ease_repos.txt`](./fair_ease_repos.txt): The lists of research software repositories provided by CESSDA and FAIR-EASE respectively.
- [`analysis_cessda.csv`](./analysis_cessda.csv) and [`analysis_fair_ease.csv`](./analysis_fair_ease.csv): CSV files containing the assessment results for each repository against the two metrics implemented at time of evaluation, for the repositories provided by CESSDA and FAIR-EASE respectively. Each file contains a column `resolved_url` with the GitHub URL, as well as a column for each metric test, named with the metric test identifier, with values `fail` or `pass` depending on whether the test was passed by the repository.
- [`assessment.ipynb`](./assessment.ipynb) and [`analysis.ipynb`](./analysis.ipynb): The scripts used for the evaluation.

## How to reproduce

The evaluation requires a local instance of f-uji, as described in the [README](../README.md#usage).

Once it is running, run the [assessment notebook](./assessment.ipynb).
This will produce a set of JSON files with the responses received for each repository in `./results`.
Please note that this folder is not tracked by Git.

Next, run the [analysis notebook](./analysis.ipynb).
This will overwrite the CSV files and produce plots.
