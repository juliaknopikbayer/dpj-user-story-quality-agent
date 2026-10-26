def check_responsible(api_data: dict) -> dict:
    """
    Checks whether the User Story has a defined responsible person
    (Responsible / Accountable person).

    API field:
    api_data["_links"]["responsible"]
    """
    responsible = api_data.get("_links", {}).get("responsible") or {}

    # The absence of a responsible person in DPJ usually has the form:
    # {"href": null}
    if not responsible.get("href"):
        return {
            "status": "missing",
            "message": "The User Story does not have an assigned responsible person.",
            "responsible": None,
        }

    responsible_info = {
        "name": responsible.get("title"),
        "href": responsible.get("href"),
    }

    return {
        "status": "found",
        "message": (
            "The User Story has an assigned responsible person: "
            f"{responsible_info['name']}."
        ),
        "responsible": responsible_info,
    }
