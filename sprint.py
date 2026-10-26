def check_sprint(api_data: dict) -> dict:
    """
    Checks whether the User Story has an assigned Sprint.

    API field:
    api_data["_links"]["sprint"]
    """
    sprint = api_data.get("_links", {}).get("sprint") or {}

    if not sprint.get("href"):
        return {
            "status": "missing",
            "message": "The User Story does not have an assigned Sprint.",
            "sprint": None,
        }

    sprint_info = {
        "title": sprint.get("title"),
        "href": sprint.get("href"),
    }

    return {
        "status": "found",
        "message": (
            f"The User Story has an assigned Sprint: "
            f"{sprint_info['title']}."
        ),
        "sprint": sprint_info,
    }
