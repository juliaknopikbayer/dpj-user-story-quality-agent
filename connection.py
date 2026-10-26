import os
import re

import requests
import urllib3
from dotenv import load_dotenv


load_dotenv()

# Temporary SSL workaround for the internal certificate.
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://dpj.int.bayer.com"
VERIFY_SSL = False


def get_work_package(activity_url: str) -> dict:
    """
    Retrieves Work Package data from DPJ based on a link to its Activity view.
    Returns the full API response as a Python dictionary.
    """
    match = re.search(r"/work_packages/(\d+)", activity_url)

    if not match:
        raise ValueError("Work Package ID was not found in the provided link.")

    work_package_id = match.group(1)
    api_url = f"{BASE_URL}/api/v3/work_packages/{work_package_id}"

    api_key = os.getenv("DPJ_API_KEY")

    if not api_key:
        raise RuntimeError(
            "DPJ_API_KEY was not found. "
            "Add the key to the .env file."
        )

    response = requests.get(
        api_url,
        headers={"Accept": "application/json"},
        auth=("apikey", api_key),
        timeout=30,
        verify=VERIFY_SSL,
    )

    response.raise_for_status()

    return response.json()


def get_api_key() -> str:
    """Returns the API key read from the .env file."""
    api_key = os.getenv("DPJ_API_KEY")

    if not api_key:
        raise RuntimeError("DPJ_API_KEY was not found in the .env file.")

    return api_key


def get_work_package_relations(work_package_id: int | str) -> dict:
    """
    Retrieves all Work Package relations, including hierarchical relations.
    """
    api_key = get_api_key()

    relations_url = (
        f"{BASE_URL}/api/v3/"
        f"work_packages/{work_package_id}/relations"
    )

    response = requests.get(
        relations_url,
        headers={"Accept": "application/json"},
        auth=("apikey", api_key),
        timeout=30,
        verify=VERIFY_SSL,
    )

    response.raise_for_status()

    return response.json()
