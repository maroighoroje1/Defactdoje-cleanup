import requests
import os
import sys
from datetime import datetime, timedelta

DEFECTDOJO_URL = os.getenv("DEFECTDOJO_URL")
DEFECTDOJO_TOKEN = os.getenv("DEFECTDOJO_TOKEN")
RETENTION_DAYS = int(os.getenv("RETENTION_DAYS", 7))

ENGAGEMENTS_TO_CLEAN = [2, 4]  

headers = {
    "Authorization": f"Token {DEFECTDOJO_TOKEN}",
    "Content-Type": "application/json",
}

cutoff_date = datetime.now() - timedelta(days=RETENTION_DAYS)
print(f"Deleting tests older than {cutoff_date.strftime('%Y-%m-%d')} (retention: {RETENTION_DAYS} days)")


def get_tests(engagement_id: int) -> list:
    tests = []
    url = f"{DEFECTDOJO_URL}/api/v2/tests/?engagement={engagement_id}&limit=100"

    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch tests for engagement {engagement_id}: {response.status_code}")
            print(response.text)
            return []

        data = response.json()
        tests.extend(data.get("results", []))
        url = data.get("next")   # handle pagination

    return tests


def delete_test(test_id: int) -> bool:
    response = requests.delete(
        f"{DEFECTDOJO_URL}/api/v2/tests/{test_id}/",
        headers=headers,
    )

    if response.status_code == 204:
        print(f"Deleted test {test_id}")
        return True
    else:
        print(f"Failed to delete test {test_id}: {response.status_code}")
        print(response.text)
        return False


def cleanup(engagement_id: int):
    print(f"\nChecking engagement {engagement_id}...")
    tests = get_tests(engagement_id)

    if not tests:
        print(f"No tests found for engagement {engagement_id}")
        return

    deleted = 0
    skipped = 0

    for test in tests:
        test_id = test["id"]
        test_date = datetime.strptime(test["target_start"], "%Y-%m-%d")
        test_title = test.get("title", f"Test {test_id}")

        if test_date < cutoff_date:
            print(f"Deleting: [{test_id}] {test_title} (date: {test_date.strftime('%Y-%m-%d')})")
            if delete_test(test_id):
                deleted += 1
        else:
            print(f"Keeping:  [{test_id}] {test_title} (date: {test_date.strftime('%Y-%m-%d')})")
            skipped += 1

    print(f"Engagement {engagement_id} — deleted: {deleted}, kept: {skipped}")


if __name__ == "__main__":
    for engagement_id in ENGAGEMENTS_TO_CLEAN:
        cleanup(engagement_id)

    print("\nCleanup complete.")
