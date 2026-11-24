# CFDE Sustainability Evaluation Agent

An agentic workflow for evaluating the quarterly submissions of Common Fund (CF) Programs to the [CFDE Workbench](https://cfde.cloud/info/dcc). The agent applies 11 sustainability criteria to each submission, scores it, assigns a sustainability status, and tracks each CF Program's progress from quarter to quarter so that emerging gaps can be identified and addressed early.

## Using the hosted dashboard

1. Open the [live dashboard](https://cfde-sustainability.github.io/CFDE-Sustainability-Evaluation-Agent.io/).
2. Choose a CF Program and a release.
3. Enter your Claude API key and start scoring. The key is sent only to the Anthropic API from your browser, is cleared from the form when the run starts and is not stored.
4. Review the per-criterion results, evidence and sources, then record any reviewer adjustments.

How it works:
1. **Choose a program**
   Start a fresh review in the dashboard.

2. **Verify the submission**
   Download the approved metadata and verify locally.

3. **Score 55 elements**
   Claude uses the submission to score the 55 elements and explains each score.

4. **Review the evidence**
   The human-in-the-loop reviewers records Yes or No, a reason and a source.

5. **Confirm the score**
   Confirm the score and save the evaluation.

## Evaluation rubric

The 11 criteria are grouped into three sections. Each criterion has five elements worth one point each (5 points per criterion, 55 in total). 

| Section | Criteria |
| --- | --- |
| **Data Context and Interoperability** | Metadata Model · Ontologies & Vocabularies · Persistent Identifiers · Overall Interoperability |
| **Data History and Reproducibility** | Processing Provenance · Sample Lineage · Versioning · Documentation |
| **Data Stewardship and Reuse** | Current Status · Long-term Home · Reuse & Support |

### Sustainability Grade

| Grade | Score Criteria |
| --- | --- |
| On track to Sustainability | Total ≥ 40 / 55 |
| Actions required to be fully sustainable| Total 30–39 |
| At risk | Total < 30, **or** Long-term Home ≤ 1 |
| Not evaluated | No CFDE submission is listed for the program |

## Contact
Maintained by the Sustainability Core. For questions, please contact us at cfdesustainability@gmail.com.
