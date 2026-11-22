# CFDE sustainability scoring

Select a Common Fund program, inspect its approved C2M2 submission, and score 55 rubric elements with evidence. The team can review individual scores and confirm the recount. Each manual request runs a fresh assessment.

## Score on the website

Open the [hosted scoring dashboard](https://yrenat.github.io/CSDE-Auto-Evaluation/), select an approved release and enter your Claude key. The browser calls Anthropic directly and starts a fresh evaluation. The release menu shows the public measurements available and when they were checked. Resolve outstanding scores in the team review section and download the JSON assessment before closing the tab.

The key stays in memory for the run. Scores and human decisions on the hosted dashboard stay in the browser tab until exported. The Python application below also supports an on-disk review history and a release watcher.

## Run the dashboard

Use Python 3.10+ on Linux or macOS. In the repository folder:

    python3 -m venv .venv
    source .venv/bin/activate
    python -m pip install -r requirements.txt
    python cfde_evaluator/dashboard.py

Open http://127.0.0.1:8765, choose a program, enter your Claude API key, and start scoring. The key is held in memory for the run. Public package measurements and rubric questions go to Anthropic. The metadata ZIP is downloaded to temporary storage. Completed assessments are saved in local SQLite.

In another terminal, start team review:

    .venv/bin/python cfde_evaluator/reviewer.py

Open http://127.0.0.1:8766 to score a completed assessment and record reasons and evidence.

## Command line

    python cfde_evaluator/evaluate.py inspect --program 4DN
    python cfde_evaluator/evaluate.py score --program 4DN
    python cfde_evaluator/evaluate.py watch --interval 3600

The score and watch commands prompt for a hidden key or use ANTHROPIC_API_KEY if set. The watch command polls for newly observed approved releases. Use --json for machine-readable scores. To inspect a downloaded 4DN package offline, run python cfde_evaluator/offline_demo.py PATH_TO_ZIP.

## GitHub Pages

Publish the docs folder from main. A scheduled GitHub Actions job refreshes public package measurements daily. Scoring requests are made live by visitors using their own Anthropic API credits. The public evidence catalogue contains release identifiers and aggregate table measurements.
