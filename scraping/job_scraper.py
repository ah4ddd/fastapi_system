import requests
import json


API_URL = "https://remoteok.com/api"


def fetch_all_jobs():
    try:
        response = requests.get(API_URL, timeout=15)
        response.raise_for_status()

        data = response.json()

        # First element is metadata
        jobs = data[1:]

        return jobs

    except Exception as e:
        print(f"Error occurred: {e}")
        return []

if __name__ == "__main__":
    jobs = fetch_all_jobs()

    print(f"\nTotal jobs returned by API: {len(jobs)}\n")

    for job in jobs:
        print(f"Position: {job.get('position')}")
        print(f"Company: {job.get('company')}")
        print(f"Location: {job.get('location')}")
        print(f"Tags: {job.get('tags')}")
        print(f"Apply URL: {job.get('apply_url')}")
        print("-" * 60)

    # Save everything
    with open("all_remoteok_jobs.json", "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=2)

    print("\nSaved all jobs to all_remoteok_jobs.json")
