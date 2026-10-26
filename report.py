import json
from datetime import datetime
from pathlib import Path


def _format_items(items: list[dict]) -> str:
    """Formats a list of missing items or items requiring review."""
    if not items:
        return "- None\n"

    lines = []

    for item in items:
        field = item.get("field", "Unknown item")
        reason = item.get("reason", "No details")
        lines.append(f"- **{field}**: {reason}")

    return "\n".join(lines) + "\n"


def save_validation_report(
    api_data: dict,
    overall_result: dict,
    ac_result: dict,
    ac_quality_result: dict,
    business_objective_result: dict,
    epic_result: dict,
    hierarchy_result: dict,
    story_points_result: dict,
    version_result: dict,
    sprint_result: dict,
    assignee_result: dict,
    responsible_result: dict,
    recommendation_result: dict | None = None,
) -> tuple[Path, Path]:
    """
    Saves two files:
    - JSON: complete validation data for the application,
    - Markdown: a report readable by the team.
    """
    work_package_id = str(api_data.get("id", "unknown"))
    subject = api_data.get("subject", "No title")
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # The folder will be created automatically if it does not exist yet.
    output_folder = Path("validation_reports")
    output_folder.mkdir(exist_ok=True)

    json_path = output_folder / f"work_package_{work_package_id}.json"
    markdown_path = output_folder / f"work_package_{work_package_id}.md"

    # All results in one structure.
    report_data = {
        "metadata": {
            "work_package_id": work_package_id,
            "subject": subject,
            "created_at": created_at,
            "source_url": api_data.get("_links", {})
            .get("self", {})
            .get("href"),
        },
        "overall": overall_result,
        "validation_results": {
            "acceptance_criteria": ac_result,
            "acceptance_criteria_quality": ac_quality_result,
            "business_objective": business_objective_result,
            "epic": epic_result,
            "hierarchy": hierarchy_result,
            "story_points": story_points_result,
            "target_version": version_result,
            "sprint": sprint_result,
            "assignee": assignee_result,
            "responsible": responsible_result,
        },
        "recommendations": recommendation_result,
    }

    # Full machine-readable result / for application use.
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(
            report_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # Helper data for the Markdown report.
    epic = epic_result.get("epic") or {}
    hierarchy = hierarchy_result.get("hierarchy") or {}
    story_points = story_points_result.get("story_points")
    version = version_result.get("version") or {}
    sprint = sprint_result.get("sprint") or {}
    assignee = assignee_result.get("assignee") or {}
    responsible = responsible_result.get("responsible") or {}

    overall_status = overall_result.get("overall_status", "Needs review")
    overall_message = overall_result.get("message", "")

    report_markdown = f"""# DPJ User Story Quality Report

## User Story

- **Work Package ID:** {work_package_id}
- **Title:** {subject}
- **Checked at:** {created_at}
- **Overall status:** **{overall_status}**
- **Summary:** {overall_message}

---

## Validation Checklist

| Check | Status | Details |
|---|---|---|
| Acceptance Criteria | {ac_result.get("status")} | {ac_result.get("message")} |
| Acceptance Criteria quality | {ac_quality_result.get("overall_quality")} | {ac_quality_result.get("summary") or ac_quality_result.get("message")} |
| Business objective | {business_objective_result.get("status")} | {business_objective_result.get("summary") or business_objective_result.get("message")} |
| Epic assignment | {epic_result.get("status")} | {epic_result.get("message")} |
| Story Points | {story_points_result.get("status")} | {story_points_result.get("message")} |
| Target Version | {version_result.get("status")} | {version_result.get("message")} |
| Sprint | {sprint_result.get("status")} | {sprint_result.get("message")} |
| Assignee | {assignee_result.get("status")} | {assignee_result.get("message")} |
| Responsible / Accountable | {responsible_result.get("status")} | {responsible_result.get("message")} |

---

## Assigned Information

- **Epic:** {epic.get("title") or "Not assigned"}
- **Parent Work Item:** {hierarchy.get("parent", {}).get("title") or "Not assigned"}
- **Story Points:** {story_points if story_points is not None else "Not assigned"}
- **Target Version:** {version.get("title") or "Not assigned"}
- **Sprint:** {sprint.get("title") or "Not assigned"}
- **Assignee:** {assignee.get("name") or "Not assigned"}
- **Responsible / Accountable person:** {responsible.get("name") or "Not assigned"}

---

## Acceptance Criteria

"""

    criteria = ac_result.get("criteria", [])

    if criteria:
        for index, criterion in enumerate(criteria, start=1):
            report_markdown += f"{index}. {criterion}\n"
    else:
        report_markdown += "_No Acceptance Criteria were found._\n"

    report_markdown += "\n---\n\n## Missing Required Information\n\n"
    report_markdown += _format_items(overall_result.get("missing_items", []))

    report_markdown += "\n---\n\n## Items Requiring Review\n\n"
    report_markdown += _format_items(overall_result.get("review_items", []))

    # Adds LLM recommendations if they were generated.
    if recommendation_result:
        report_markdown += "\n---\n\n## Recommended Improvements\n\n"
        report_markdown += (
            f"{recommendation_result.get('summary', 'No summary available.')}\n"
        )

        recommendations = recommendation_result.get("recommendations", [])

        if recommendations:
            for index, recommendation in enumerate(recommendations, start=1):
                report_markdown += f"""
### {index}. {recommendation.get("area", "Improvement")}

- **Priority:** {recommendation.get("priority", "medium")}
- **Issue:** {recommendation.get("issue", "")}
- **Recommendation:** {recommendation.get("recommendation", "")}

"""

        suggested_description = recommendation_result.get(
            "suggested_description"
        )

        if suggested_description:
            report_markdown += f"""### Suggested User Story Description

         ```text
        {suggested_description}
        """ 
    suggested_ac = recommendation_result.get(
        "suggested_acceptance_criteria",
        [],
    )

    if suggested_ac:
        report_markdown += "### Suggested Acceptance Criteria\\n\\n"

        for index, criterion in enumerate(suggested_ac, start=1):
            report_markdown += f"{index}. {criterion}\\n"

    with open(markdown_path, "w", encoding="utf-8") as file:
        file.write(report_markdown)

    return json_path, markdown_path
