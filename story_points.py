def check_story_points(api_data: dict) -> dict:
    """
    Checks whether the User Story has a positive Story Points estimate assigned.

    Expected API field:
    api_data["storyPoints"]
    """
    story_points = api_data.get("storyPoints")

    # No value in the API.
    if story_points is None:
        return {
            "status": "missing",
            "message": "The User Story does not have Story Points assigned.",
            "story_points": None,
        }

    # A value of 0 or a negative value is not a valid estimate.
    if not isinstance(story_points, (int, float)) or story_points <= 0:
        return {
            "status": "needs_review",
            "message": (
                "The Story Points field exists but contains an invalid value: "
                f"{story_points}."
            ),
            "story_points": story_points,
        }

    return {
        "status": "found",
        "message": f"The User Story has Story Points assigned: {story_points}.",
        "story_points": story_points,
    }
