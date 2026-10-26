DPJ User Story Quality Agent is an AI-assisted Python application that reviews a selected User Story in the DPJ application.

It retrieves User Story data through the DPJ API and validates whether mandatory planning and delivery information is complete and ready for sprint planning or development.

The agent checks:

- Acceptance Criteria availability and quality
- Epic or parent work-item relationship
- Business objective, value, or expected outcome
- Story Points
- Target Version or Sprint
- Assignee
- Responsible / Accountable person

For each reviewed User Story, the agent returns:

- Overall status: `Complete`, `Incomplete`, or `Needs review`
- Completed validation checks
- Missing mandatory information
- Items requiring review
- Deterministic actionable recommendations for missing fields
- AI-generated suggestions for improving the User Story description and Acceptance Criteria when needed

The application generates both JSON and Markdown validation reports.
