from acceptance_criteria import * 
from parent_link import *
from story_points import *
from version import *
from sprint import *
from assignee import *
from accountable import *
from validator import * 
from summary import *
from recommendation import *
from report import *
import json
from connection import get_work_package
import sys


if len(sys.argv) > 1:
    activity_url = sys.argv[1].strip()
else:
    activity_url = input(
        "Paste the link to the DPJ Work Package: "
    ).strip()

if not activity_url:
    raise ValueError("No Work Package link was provided.")


data = get_work_package(activity_url)

# print("\n" + "=" * 70)
# print("LINKS AVAILABLE IN THE API RESPONSE")
# print("=" * 70)

# print(
#     json.dumps(
#         data.get("_links", {}),
#         indent=2,
#         ensure_ascii=False,
#     )
# )


# print(f"ID: {data.get('id')}")
# print(f"Subject: {data.get('subject')}")


def acceptance_criteria_node(): 
    # Acceptance Criteria analysis from the field:
    # data["description"]["raw"]
    result = check_acceptance_criteria(data)

    print("\n" + "=" * 70)
    print("ACCEPTANCE CRITERIA VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Found heading: {result['heading']}")
    print(f"Match confidence: {result['confidence']}%")

    if result["criteria"]:
        print("\nFound criteria:")

        for number, criterion in enumerate(result["criteria"], start=1):
            print(f"{number}. {criterion}")

    elif result["raw_content"]:
        print("\nSection content requiring review:")
        print(result["raw_content"])

    ac_result = result
    ac_quality_result = check_acceptance_criteria_quality_with_llm(
        api_data=data,
        ac_result=ac_result,
    )

    print("\n" + "=" * 70)
    print("LLM ACCEPTANCE CRITERIA QUALITY ASSESSMENT RESULT")
    print("=" * 70)

    print(f"Execution status: {ac_quality_result['status']}")
    print(f"Overall assessment: {ac_quality_result['overall_quality']}")
    print(f"Summary: {ac_quality_result['summary']}")

    for assessment in ac_quality_result["criteria_assessment"]:
        print("\n" + "-" * 70)
        print(f"Criterion {assessment.get('number')}:")
        print(assessment.get("criterion"))
        print(f"Status: {assessment.get('status')}")
        print(f"Related to User Story: {assessment.get('relevant_to_story')}")
        print(f"Testable: {assessment.get('testable')}")

        issues = assessment.get("issues", [])

        if issues:
            print("Issues:")

            for issue in issues:
                print(f"- {issue}")

        recommendation = assessment.get("recommendation", "")

        if recommendation:
            print(f"Recommendation: {recommendation}")

    return ac_result, ac_quality_result


def parent_link_node():
    hierarchy_result = check_parent_or_epic(data)

    print("\n" + "=" * 70)
    print("EPIC / PARENT VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {hierarchy_result['status']}")
    print(f"Message: {hierarchy_result['message']}")

    if hierarchy_result["parent"]:
        parent = hierarchy_result["parent"]

        print("\nDirect parent:")
        print(f"- ID: {parent['id']}")
        print(f"- Name: {parent['title']}")
        print(f"- API href: {parent['href']}")

    if hierarchy_result["ancestors"]:
        print("\nParent items in the hierarchy:")

        for ancestor in hierarchy_result["ancestors"]:
            print(
                f"- ID: {ancestor['id']} | "
                f"Name: {ancestor['title']} | "
                f"API: {ancestor['href']}"
            )



    epic_result = check_epic_assignment(api_data=data)

    print("\n" + "=" * 70)
    print("EPIC VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {epic_result['status']}")
    print(f"Information: {epic_result['message']}")

    if epic_result["epic"]:
        epic = epic_result["epic"]

        print("\nFOUND EPIC:")
        print(f"ID: {epic['id']}")
        print(f"Name: {epic['title']}")
        print(f"Type: {epic['type']}")
        print(f"API endpoint: {BASE_URL}{epic['href']}")

    print("\nCHECKED ANCESTORS:")

    for ancestor in epic_result["checked_ancestors"]:
        print(
            f"- ID: {ancestor['id']} | "
            f"Type: {ancestor['type']} | "
            f"Name: {ancestor['title']}"
        )

        if "error" in ancestor:
            print(f"  Retrieval error: {ancestor['error']}")
    return hierarchy_result, epic_result


def story_points_node(): 
    story_points_result = check_story_points(data)

    print("\n" + "=" * 70)
    print("STORY POINTS VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {story_points_result['status']}")
    print(f"Information: {story_points_result['message']}")
    print(f"Story Points: {story_points_result['story_points']}")

    return story_points_result

def version_node(): 
    version_result = check_version(data)
    

    print("\n" + "=" * 70)
    print("TARGET VERSION VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {version_result['status']}")
    print(f"Information: {version_result['message']}")

    if version_result["version"]:
        print(f"Name: {version_result['version']['title']}")
        print(f"API: {version_result['version']['href']}")

    return version_result
    
def sprint_node():
    sprint_result = check_sprint(data)
    print("\n" + "=" * 70)
    print("SPRINT VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {sprint_result['status']}")
    print(f"Information: {sprint_result['message']}")

    if sprint_result["sprint"]:
        print(f"Name: {sprint_result['sprint']['title']}")
        print(f"API: {sprint_result['sprint']['href']}")

    return sprint_result

def assignee_node():
    assignee_result = check_assignee(data)

    print("\n" + "=" * 70)
    print("ASSIGNEE VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {assignee_result['status']}")
    print(f"Information: {assignee_result['message']}")

    if assignee_result["assignee"]:
        assignee = assignee_result["assignee"]

        print(f"Name: {assignee['name']}")
        print(f"API: {assignee['href']}")

    return assignee_result

def accountable_node(): 
    responsible_result = check_responsible(data)

    print("\n" + "=" * 70)
    print("RESPONSIBLE / ACCOUNTABLE VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {responsible_result['status']}")
    print(f"Information: {responsible_result['message']}")

    if responsible_result["responsible"]:
        responsible = responsible_result["responsible"]

        print(f"Name: {responsible['name']}")
        print(f"API: {responsible['href']}")

    return responsible_result

def llm_check_node():
    business_objective_result = check_business_objective_with_llm(data)

    print("\n" + "=" * 70)
    print("BUSINESS OBJECTIVE VALIDATION RESULT")
    print("=" * 70)

    print(f"Status: {business_objective_result['status']}")
    print(f"Information: {business_objective_result['message']}")
    print(f"Objective found: {business_objective_result['objective_found']}")
    print(
        "Business value found: "
        f"{business_objective_result['business_value_found']}"
    )
    print(
        "Expected outcome found: "
        f"{business_objective_result['expected_outcome_found']}"
    )
    print(f"\nSummary: {business_objective_result['summary']}")

    if business_objective_result["evidence"]:
        print("\nEvidence:")

        for item in business_objective_result["evidence"]:
            print(f"- {item}")

    if business_objective_result["recommendation"]:
        print("\nRecommendation:")
        print(business_objective_result["recommendation"])

    return business_objective_result

def summary(
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
) -> dict:
    """
    Creates a deterministic summary of User Story quality.

    Final status:
    - Complete
    - Incomplete
    - Needs review
    """
    overall_result = create_overall_summary(
        ac_result=ac_result,
        ac_quality_result=ac_quality_result,
        business_objective_result=business_objective_result,
        hierarchy_result=hierarchy_result,
        story_points_result=story_points_result,
        version_result=version_result,
        sprint_result=sprint_result,
        assignee_result=assignee_result,
        responsible_result=responsible_result,
    )

    print("\n" + "=" * 70)
    print("OVERALL USER STORY STATUS")
    print("=" * 70)

    print(f"Status: {overall_result['overall_status']}")
    print(f"Information: {overall_result['message']}")

    if overall_result.get("completed_items"):
        print("\nCOMPLETED ITEMS:")

        for item in overall_result["completed_items"]:
            print(f"- {item}")

    if overall_result.get("missing_items"):
        print("\nMISSING ITEMS:")

        for item in overall_result["missing_items"]:
            print(f"- {item['field']}: {item['reason']}")
            print(f"  Recommendation: {item['recommendation']}")

    if overall_result.get("review_items"):
        print("\nITEMS REQUIRING REVIEW:")

        for item in overall_result["review_items"]:
            print(f"- {item['field']}: {item['reason']}")

    return overall_result

def recommendation_node(
    overall_result: dict,
    ac_result: dict,
    ac_quality_result: dict,
    business_objective_result: dict,
) -> dict:
    """
    Generates LLM suggestions only for User Story description
    and Acceptance Criteria when content improvements are required.

    Deterministic recommendations for missing administrative fields
    are already included in overall_result.
    """
    recommendation_result = generate_user_story_recommendations_with_llm(
        api_data=data,
        overall_result=overall_result,
        ac_result=ac_result,
        ac_quality_result=ac_quality_result,
        business_objective_result=business_objective_result,
    )

    print("\n" + "=" * 70)
    print("USER STORY CONTENT IMPROVEMENT SUGGESTIONS")
    print("=" * 70)

    print(f"Status: {recommendation_result['status']}")
    print(f"Information: {recommendation_result['message']}")
    print(f"Summary: {recommendation_result['summary']}")

    if recommendation_result["suggested_description"]:
        print("\nSUGGESTED USER STORY DESCRIPTION:")
        print(recommendation_result["suggested_description"])

    if recommendation_result["suggested_acceptance_criteria"]:
        print("\nSUGGESTED ACCEPTANCE CRITERIA:")

        for index, criterion in enumerate(
            recommendation_result["suggested_acceptance_criteria"],
            start=1,
        ):
            print(f"{index}. {criterion}")

    return recommendation_result

# 1. Acceptance Criteria must be checked before their quality is assessed by the LLM.
ac_result, ac_quality_result = acceptance_criteria_node()

# 2. Business objective — assessment by the LLM.
business_objective_result = llm_check_node()

# 3. Epic / hierarchy.
hierarchy_result, epic_result = parent_link_node()

# 4. Fields checked deterministically through the DPJ API.
story_points_result = story_points_node()
version_result = version_node()
sprint_result = sprint_node()
assignee_result = assignee_node()
responsible_result = accountable_node()

# 5. Deterministic summary of all results.
overall_result = summary(
    ac_result=ac_result,
    ac_quality_result=ac_quality_result,
    business_objective_result=business_objective_result,
    epic_result=epic_result,
    hierarchy_result=hierarchy_result,
    story_points_result=story_points_result,
    version_result=version_result,
    sprint_result=sprint_result,
    assignee_result=assignee_result,
    responsible_result=responsible_result,
)

recommendation_result = recommendation_node(
    overall_result=overall_result,
    ac_result=ac_result,
    ac_quality_result=ac_quality_result,
    business_objective_result=business_objective_result,
)


json_file, markdown_file = save_validation_report(
    api_data=data,
    overall_result=overall_result,
    ac_result=ac_result,
    ac_quality_result=ac_quality_result,
    business_objective_result=business_objective_result,
    epic_result=epic_result,
    hierarchy_result=hierarchy_result,
    story_points_result=story_points_result,
    version_result=version_result,
    sprint_result=sprint_result,
    assignee_result=assignee_result,
    responsible_result=responsible_result,
    recommendation_result=recommendation_result,
)

print("\n" + "=" * 70)
print("REPORT HAS BEEN SAVED")
print("=" * 70)
print(f"JSON: {json_file.resolve()}")
print(f"Team report: {markdown_file.resolve()}")
