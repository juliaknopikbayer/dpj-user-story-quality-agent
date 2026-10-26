def create_overall_summary(
    ac_result: dict,
    ac_quality_result: dict,
    business_objective_result: dict,
    hierarchy_result: dict,
    story_points_result: dict,
    version_result: dict,
    sprint_result: dict,
    assignee_result: dict,
    responsible_result: dict,
) -> dict:
    """
    Creates the final User Story quality status.

    Possible final statuses:
    - Complete
    - Incomplete
    - Needs review

    Target Version OR Sprint is required:
    at least one of these fields must be assigned.

    Every missing item or item requiring review receives a deterministic,
    actionable recommendation.
    """

    recommendations = {
        "Acceptance Criteria": (
            "Add an Acceptance Criteria section using the heading "
            "'## Acceptance Criteria' and include at least one clear, "
            "testable criterion."
        ),
        "Acceptance Criteria quality": (
            "Review and update the Acceptance Criteria so that each criterion "
            "is relevant, specific, observable, and testable."
        ),
        "Business objective": (
            "Update the User Story description to clearly state the intended "
            "objective, business value, or expected outcome."
        ),
        "Epic or parent work item": (
            "Assign the User Story to an Epic or link it to a parent work item."
        ),
        "Story Points": (
            "Assign a positive Story Points estimate to the User Story."
        ),
        "Target Version or Sprint": (
            "Assign either a Target Version or a Sprint to the User Story."
        ),
        "Assignee": (
            "Assign an Assignee responsible for implementing the User Story."
        ),
        "Responsible / Accountable person": (
            "Assign a Responsible or Accountable person to the User Story."
        ),
    }

    def get_recommendation(field: str) -> str:
        """Returns a deterministic recommendation for a validation field."""
        return recommendations.get(
            field,
            "Review the validation result and update the User Story accordingly.",
        )

    checks = [
        {
            "name": "Acceptance Criteria",
            "result": ac_result,
        },
        {
            "name": "Acceptance Criteria quality",
            "result": ac_quality_result,
        },
        {
            "name": "Business objective",
            "result": business_objective_result,
        },
        {
            "name": "Epic or parent work item",
            "result": hierarchy_result,
        },
        {
            "name": "Story Points",
            "result": story_points_result,
        },
        {
            "name": "Assignee",
            "result": assignee_result,
        },
        {
            "name": "Responsible / Accountable person",
            "result": responsible_result,
        },
    ]

    missing_items = []
    review_items = []
    completed_items = []

    for check in checks:
        name = check["name"]
        result = check["result"]

        status = result.get("status")
        overall_quality = result.get("overall_quality")

        # Missing required data: Incomplete.
        if status in ["missing", "empty"]:
            missing_items.append(
                {
                    "field": name,
                    "reason": result.get(
                        "message",
                        "Required information is missing.",
                    ),
                    "recommendation": get_recommendation(name),
                }
            )
            continue

        # Special Acceptance Criteria quality check using the LLM.
        if name == "Acceptance Criteria quality":
            if overall_quality in ["needs_review", "invalid", None]:
                review_items.append(
                    {
                        "field": name,
                        "reason": (
                            result.get("summary")
                            or result.get("message")
                            or "Acceptance Criteria require review."
                        ),
                        "recommendation": get_recommendation(name),
                    }
                )
                continue

        # The Business Objective is assessed by the LLM.
        if name == "Business objective" and status == "needs_review":
            review_items.append(
                {
                    "field": name,
                    "reason": (
                        result.get("summary")
                        or result.get("message")
                        or "The business objective requires review."
                    ),
                    "recommendation": get_recommendation(name),
                }
            )
            continue

        # Other cases requiring manual review.
        if status == "needs_review":
            review_items.append(
                {
                    "field": name,
                    "reason": result.get(
                        "message",
                        "Requires review.",
                    ),
                    "recommendation": get_recommendation(name),
                }
            )
            continue

        # A found status means that the check passed.
        if status == "found":
            completed_items.append(name)
            continue

        # An unexpected status should not automatically mean Complete.
        review_items.append(
            {
                "field": name,
                "reason": (
                    f"Unexpected validation status: {status}. "
                    "Check the result manually."
                ),
                "recommendation": get_recommendation(name),
            }
        )

    # Target Version OR Sprint:
    # at least one of these fields must have status "found".
    version_status = version_result.get("status")
    sprint_status = sprint_result.get("status")

    if version_status == "found" or sprint_status == "found":
        completed_items.append("Target Version or Sprint")

    elif version_status in ["missing", "empty"] and sprint_status in [
        "missing",
        "empty",
    ]:
        missing_items.append(
            {
                "field": "Target Version or Sprint",
                "reason": (
                    "The User Story has neither an assigned Target Version "
                    "nor an assigned Sprint."
                ),
                "recommendation": get_recommendation(
                    "Target Version or Sprint"
                ),
            }
        )

    else:
        review_items.append(
            {
                "field": "Target Version or Sprint",
                "reason": (
                    "Neither Target Version nor Sprint was confirmed as assigned. "
                    "Check both fields manually."
                ),
                "recommendation": get_recommendation(
                    "Target Version or Sprint"
                ),
            }
        )

    # Priority 1: required information is missing.
    if missing_items:
        return {
            "overall_status": "Incomplete",
            "message": (
                "The User Story is incomplete because "
                f"{len(missing_items)} required items are missing."
            ),
            "completed_items": completed_items,
            "missing_items": missing_items,
            "review_items": review_items,
        }

    # Priority 2: all data exists, but some information requires review.
    if review_items:
        return {
            "overall_status": "Needs review",
            "message": (
                "The User Story contains all required information, "
                "but some information requires review."
            ),
            "completed_items": completed_items,
            "missing_items": [],
            "review_items": review_items,
        }

    # All rules have been met.
    return {
        "overall_status": "Complete",
        "message": (
            "The User Story contains all required information "
            "and has passed the quality check."
        ),
        "completed_items": completed_items,
        "missing_items": [],
        "review_items": [],
    }
