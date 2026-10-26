def check_assignee(api_data: dict) -> dict:
    """
    Checks whether the User Story has a defined Assignee.

    API field:
    api_data["_links"]["assignee"]
    """
    assignee = api_data.get("_links", {}).get("assignee") or {}

    # In DPJ, the absence of an assigned person usually means:
    # {"href": null}
    if not assignee.get("href"):
        return {
            "status": "missing",
            "message": "The User Story does not have an assigned Assignee.",
            "assignee": None,
        }

    assignee_info = {
        "name": assignee.get("title"),
        "href": assignee.get("href"),
    }

    return {
        "status": "found",
        "message": (
            f"The User Story has an assigned Assignee: "
            f"{assignee_info['name']}."
        ),
        "assignee": assignee_info,
    }
