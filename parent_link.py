from connection import * 
import requests

def check_parent_or_epic(api_data: dict) -> dict:
    """
    Checks the hierarchical relationship of the User Story.

    The condition is met if:
    - a direct parent exists, or
    - there is at least one parent item in ancestors.

    Does not use the /ancestors endpoint because DPJ returns this information
    directly in api_data["_links"]["ancestors"].
    """
    links = api_data.get("_links", {})

    parent = links.get("parent")
    ancestors = links.get("ancestors", [])

    parent_info = None

    if parent and parent.get("href"):
        parent_info = {
            "id": parent.get("displayId"),
            "title": parent.get("title"),
            "href": parent.get("href"),
        }

    ancestors_info = []

    for ancestor in ancestors:
        ancestors_info.append(
            {
                "id": ancestor.get("displayId"),
                "title": ancestor.get("title"),
                "href": ancestor.get("href"),
            }
        )

    # Requirement: Epic OR designated parent work item.
    # A parent exists, so the story has the required hierarchical link.
    if parent_info:
        return {
            "status": "found",
            "message": (
                "The User Story has an assigned parent work item: "
                f"{parent_info['title']}."
            ),
            "has_parent": True,
            "parent": parent_info,
            "ancestors": ancestors_info,
        }

    # Theoretically possible: no direct parent,
    # but the API returns items higher in the hierarchy.
    if ancestors_info:
        return {
            "status": "found",
            "message": (
                "The User Story has parent items in the hierarchy, "
                "but the direct parent was not returned."
            ),
            "has_parent": False,
            "parent": None,
            "ancestors": ancestors_info,
        }

    return {
        "status": "missing",
        "message": (
            "The User Story does not have an assigned parent or Epic "
            "in the available hierarchy."
        ),
        "has_parent": False,
        "parent": None,
        "ancestors": [],
    }


def check_epic_assignment(api_data: dict) -> dict:
    """
    Checks whether the Work Package has either:
    - a direct parent work item, or
    - an Epic anywhere in its hierarchy.

    This satisfies the requirement: Epic OR parent work item.
    """
    links = api_data.get("_links", {})

    parent = links.get("parent") or {}
    ancestors = links.get("ancestors", [])

    # A direct parent is sufficient: Epic OR parent work item.
    if parent.get("href"):
        parent_info = {
            "id": parent.get("displayId"),
            "title": parent.get("title"),
            "href": parent.get("href"),
        }

        return {
            "status": "found",
            "message": (
                "The User Story has an assigned parent work item: "
                f"{parent_info['title']}."
            ),
            "relationship_type": "parent",
            "parent": parent_info,
            "epic": None,
            "checked_ancestors": [],
        }

    # No direct parent exists, so check whether an Epic exists in the hierarchy.
    if not ancestors:
        return {
            "status": "missing",
            "message": (
                "The User Story has neither an assigned parent work item "
                "nor an Epic in the hierarchy."
            ),
            "relationship_type": None,
            "parent": None,
            "epic": None,
            "checked_ancestors": [],
        }

    checked_ancestors = []
    epic = None

    for ancestor_link in ancestors:
        href = ancestor_link.get("href")

        if not href:
            continue

        try:
            # Retrieves ancestor data rather than data for the current User Story.
            ancestor_data = get_work_package(href)

            work_package_type = (
                ancestor_data
                .get("_links", {})
                .get("type", {})
                .get("title", "")
            )

            ancestor_info = {
                "id": ancestor_data.get("id"),
                "title": ancestor_data.get("subject"),
                "type": work_package_type,
                "href": href,
            }

            checked_ancestors.append(ancestor_info)

            if work_package_type.strip().casefold() == "epic":
                epic = ancestor_info
                break

        except requests.exceptions.RequestException as error:
            checked_ancestors.append(
                {
                    "id": ancestor_link.get("displayId"),
                    "title": ancestor_link.get("title"),
                    "type": None,
                    "href": href,
                    "error": str(error),
                }
            )

    if epic:
        return {
            "status": "found",
            "message": (
                "The User Story is assigned to the Epic: "
                f"{epic['title']}."
            ),
            "relationship_type": "epic",
            "parent": None,
            "epic": epic,
            "checked_ancestors": checked_ancestors,
        }

    return {
        "status": "missing",
        "message": (
            "The User Story has neither an assigned parent work item "
            "nor an Epic in the hierarchy."
        ),
        "relationship_type": None,
        "parent": None,
        "epic": None,
        "checked_ancestors": checked_ancestors,
    }
