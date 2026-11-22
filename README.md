# CFDE sustainability scoring

Select a Common Fund program, inspect its approved C2M2 submission, and score 55 rubric elements with evidence. The team can review individual scores and confirm the recount. Each manual request runs a fresh assessment.

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

Publish the docs folder from main. The project page displays the scoring rubric, describes the workflow, and links to the local dashboard. Python services and credentials stay on the user's computer.
