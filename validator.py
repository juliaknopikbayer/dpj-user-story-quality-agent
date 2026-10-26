import json
import re

from llm.mGA import chat

def _parse_llm_json(raw_response: str) -> dict:
    """
    Converts the LLM response into a Python dictionary.

    Supports:
    - plain JSON,
    - JSON in a Markdown ```json ... ``` block,
    - additional text before the JSON.
    """
    if raw_response is None:
        raise RuntimeError("LLM returned None.")

    if not isinstance(raw_response, str):
        raise RuntimeError(
            f"LLM returned an unexpected type: {type(raw_response).__name__}"
        )

    cleaned_response = raw_response.strip()

    if not cleaned_response:
        raise RuntimeError("LLM returned an empty response.")

    # Removes the opening Markdown block, e.g. ```json
    cleaned_response = re.sub(
        r"^```(?:json)?\s*",
        "",
        cleaned_response,
        flags=re.IGNORECASE,
    )

    # Removes the closing Markdown block, e.g. ```
    cleaned_response = re.sub(
        r"\\\\s*```$",
        "",
        cleaned_response,
    ).strip()

    # Searches for the first JSON object in the response.
    json_start = cleaned_response.find("{")

    if json_start == -1:
        raise RuntimeError(
            "LLM did not return a JSON object.\n"
            f"LLM response:\n{raw_response}"
        )

    possible_json = cleaned_response[json_start:]

    try:
        decoder = json.JSONDecoder()
        parsed_json, _ = decoder.raw_decode(possible_json)

        if not isinstance(parsed_json, dict):
            raise RuntimeError("LLM returned JSON, but it is not an object.")

        return parsed_json

    except json.JSONDecodeError as error:
        raise RuntimeError(
            "Failed to read the JSON returned by the LLM.\n"
            f"Error: {error}\n\n"
            f"Raw LLM response:\n{raw_response}"
        ) from error


def check_business_objective_with_llm(api_data: dict) -> dict:
    """
    Checks using an LLM whether the User Story description contains:
    - an intended objective,
    - business value,
    - an expected outcome.

    Analyses only the field:
    api_data["description"]["raw"]

    Statuses:
    - found: the description contains a sufficiently clear objective / value / outcome,
    - missing: the description is empty,
    - needs_review: the description exists, but the objective is unclear, too general,
      or incomplete.
    """
    subject = api_data.get("subject", "").strip()
    description = api_data.get("description", {}).get("raw", "").strip()

    # Deterministic check — do not call the LLM without a description.
    if not description:
        return {
            "status": "missing",
            "message": "The User Story has no description, so it does not contain a business objective.",
            "objective_found": False,
            "business_value_found": False,
            "expected_outcome_found": False,
            "summary": None,
            "recommendation": (
                "Add a User Story description containing an objective, business value, "
                "or expected outcome."
            ),
        }

    # Optionally limit the length to avoid sending a very long description.
    description_for_review = description[:6000]

    system_prompt = """
You are an Agile Business Analyst reviewing a User Story.

Your task is to decide whether the supplied User Story description clearly
states at least one of the following:
1. the intended objective or goal,
2. the business value,
3. the expected outcome.

Evaluate only the information provided. Do not invent missing requirements.

Return only valid JSON. Do not use Markdown. Do not use code fences.
Return only valid JSON. Do not use Markdown. Do not use code fences.
Your response must begin with { and end with }.
Do not write any text before or after the JSON object.
Use JSON booleans: true or false, never True or False.

"""

    prompt = f"""
Review this User Story.

Title:
{subject}

Description:
{description_for_review}

Return exactly this JSON structure:

{{
  "objective_found": true,
  "business_value_found": true,
  "expected_outcome_found": true,
  "overall_status": "found",
  "summary": "Short explanation of what was found or what is unclear.",
  "evidence": [
    "Short quote or paraphrase from the description supporting the assessment."
  ],
  "recommendation": "Actionable recommendation. Use an empty string if no improvement is needed."
}}

Rules:
- Set overall_status to "found" if the description clearly contains an intended
  objective, business value, or expected outcome.
- Set overall_status to "needs_review" if the description exists but is vague,
  unclear, technical-only, or does not sufficiently state a goal/value/outcome.
- Do not use "missing" because the Python code handles empty descriptions.
- Keep summary and recommendation concise.
"""

    try:
        raw_llm_response = chat(
            prompt=prompt,
            system=system_prompt,
        )

        print("\n" + "=" * 70)
        print("RAW RESPONSE FROM THE LLM (repr)")
        print("=" * 70)
        print(repr(raw_llm_response))

        llm_result = _parse_llm_json(raw_llm_response)

        return {
            "status": llm_result.get("overall_status", "needs_review"),
            "message": "The business objective assessment was performed by the LLM.",
            "objective_found": bool(llm_result.get("objective_found")),
            "business_value_found": bool(llm_result.get("business_value_found")),
            "expected_outcome_found": bool(
                llm_result.get("expected_outcome_found")
            ),
            "summary": llm_result.get("summary"),
            "evidence": llm_result.get("evidence", []),
            "recommendation": llm_result.get("recommendation", ""),
        }

    except (json.JSONDecodeError, RuntimeError, KeyError) as error:
        return {
            "status": "needs_review",
            "message": (
                "The business objective could not be assessed conclusively by the LLM."
            ),
            "objective_found": False,
            "business_value_found": False,
            "expected_outcome_found": False,
            "summary": str(error),
            "evidence": [],
            "recommendation": (
                "Review the description manually or repeat the analysis."
            ),
        }

