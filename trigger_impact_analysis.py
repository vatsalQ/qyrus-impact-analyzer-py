#!/usr/bin/env python3

import os
import sys
import json
import requests
import time


def main():
    # Get environment variables
    impact_api_url = os.environ.get('IMPACT_API_URL')
    api_access_token = os.environ.get('API_ACCESS_TOKEN')
    project_id = os.environ.get('PROJECT_ID')
    source_branch = os.environ.get('SOURCE_BRANCH')
    target_branch = os.environ.get('TARGET_BRANCH')
    github_token = os.environ.get('GITHUB_TOKEN')

    # PR metadata
    pr_number = os.environ.get('PR_NUMBER')
    pr_title = os.environ.get('PR_TITLE')
    pr_author = os.environ.get('PR_AUTHOR')
    repo_full_name = os.environ.get('REPO_FULL_NAME')
    print(f"REPO FULL NAME: {repo_full_name}")
    repo_url = f"https://github.com/{repo_full_name}"
    print(f"REPO URL: {repo_url}")

    # Read structured diff from file
    try:
        with open('structured_diff.json', 'r', encoding='utf-8') as f:
            structured_diff = json.load(f)
        print(
            f"Read structured diff with {len(structured_diff.get('files', []))} files"
        )
    except Exception as e:
        print(f"Error reading structured diff file: {e}")
        sys.exit(1)

    # Validate required parameters
    required_params = {
        'IMPACT_API_URL': impact_api_url,
        'API_ACCESS_TOKEN': api_access_token,
        'PROJECT_ID': project_id,
        'SOURCE_BRANCH': source_branch,
        'TARGET_BRANCH': target_branch,
    }

    for param_name, param_value in required_params.items():
        if not param_value:
            print(
                f"Error: Missing required environment variable: {param_name}")
            sys.exit(1)

    if not structured_diff or not structured_diff.get('files'):
        print("Error: Structured diff is empty or invalid")
        sys.exit(1)

    # TODO: Remove older payload: Build request payload
    # payload = {
    #     'job_id': project_id,
    #     'source_branch': source_branch,
    #     'target_branch': target_branch,
    #     'structured_diff':
    #     structured_diff,  # Use structured diff instead of raw diff
    #     'github_token': github_token,
    #     'pr_metadata': {
    #         'pr_number': pr_number,
    #         'pr_title': pr_title,
    #         'pr_author': pr_author,
    #         'repository': repo_full_name
    #     }
    # }

    payload = {
        'project_id': project_id,
        'source_branch': source_branch,
        'target_branch': target_branch,
        'structured_diff': structured_diff,
        'github_token': github_token,
        'pr_metadata': {
            'pr_number': pr_number,
            'pr_title': pr_title,
            'pr_author': pr_author,
            'repository': repo_full_name
        },
        "repo_url": repo_url
    }

    # Headers with custom access token
    headers = {
        'Content-Type': 'application/json',
        'X-API-Access-Token': api_access_token
    }

    # Send request to Impact Analyzer API
    try:
        print(f"Sending impact analysis request to {impact_api_url}")
        start_time = time.time()
        response = requests.post(
            impact_api_url,
            json=payload,
            headers=headers,
            timeout=30  # 30 seconds timeout
        )
        elapsed_time = time.time() - start_time

        # Print status code and timing
        print(
            f"Request completed in {elapsed_time:.2f}s with status code {response.status_code}"
        )

        # Check response
        if response.status_code in [200, 201, 202]:
            try:
                result = response.json()
                job_id = result.get('impact_analysis_id')
                print(
                    f"Impact analysis job created successfully. Job ID: {job_id}"
                )
                print(f"Response: {json.dumps(result, indent=2)}")

                # Save job ID to output file for potential later use
                with open('impact_analysis_job.txt', 'w') as f:
                    f.write(job_id)

                # Output for GitHub Actions
                print(f"::set-output name=impact_analysis_id::{job_id}")
            except json.JSONDecodeError:
                print("Warning: Could not parse response as JSON")
                print(f"Response text: {response.text[:200]}...")
        else:
            print(f"Error: API returned status code {response.status_code}")
            print(f"Response: {response.text[:500]}...")
            sys.exit(1)

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
