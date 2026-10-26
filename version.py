def check_version(api_data: dict) -> dict:
    """
    Checks whether the User Story has an assigned Target Version.

    API field:
    api_data["_links"]["version"]
    """
    version = api_data.get("_links", {}).get("version") or {}

    if not version.get("href"):
        return {
            "status": "missing",
            "message": "The User Story does not have an assigned Target Version.",
            "version": None,
        }

    version_info = {
        "title": version.get("title"),
        "href": version.get("href"),
    }

    return {
        "status": "found",
        "message": (
            f"The User Story has an assigned Target Version: "
            f"{version_info['title']}."
        ),
        "version": version_info,
    }
