#!/usr/bin/env python3

import os
import sys
import json
import requests
import time
from generate_diff import get_full_git_diff, get_commit_ids


def main():
   
    impact_api_url = os.environ.get('IMPACT_API_URL')
    api_access_token = os.environ.get('API_ACCESS_TOKEN')
    project_id = os.environ.get('PROJECT_ID')

    # QAPI Integration (mapped from old workspace fields)
    qapi_workspace_name = os.environ.get('WORKSPACE_NAME') or os.environ.get('QAPI_WORKSPACE_NAME')
    qapi_suite_name = os.environ.get('SUITE_NAME') or os.environ.get('QAPI_SUITE_NAME')
    qapi_environment_name = os.environ.get('ENVIRONMENT_NAME') or os.environ.get('QAPI_ENVIRONMENT_NAME')
    qapi_username = os.environ.get('USERNAME') or os.environ.get('QAPI_USERNAME')
    qapi_password = os.environ.get('PASSWORD') or os.environ.get('QAPI_PASSWORD')

    # Qyrus Integration
    qyrus_api_token = os.environ.get('QYRUS_API_TOKEN')
    team_name = os.environ.get('TEAM_NAME')

    # Web/Mobile/Desktop Integration
    web_project_name = os.environ.get('WEB_PROJECT_NAME')
    web_suite_name = os.environ.get('WEB_SUITE_NAME')
    web_run_configuration_name = os.environ.get('WEB_RUN_CONFIGURATION_NAME')

    mobile_project_name = os.environ.get('MOBILE_PROJECT_NAME')
    mobile_suite_name = os.environ.get('MOBILE_SUITE_NAME')
    mobile_run_configuration_name = os.environ.get('MOBILE_RUN_CONFIGURATION_NAME')

    desktop_project_name = os.environ.get('DESKTOP_PROJECT_NAME')
    desktop_suite_name = os.environ.get('DESKTOP_SUITE_NAME')
    desktop_run_configuration_name = os.environ.get('DESKTOP_RUN_CONFIGURATION_NAME')

    source_branch = os.environ.get('SOURCE_BRANCH')
    target_branch = os.environ.get('TARGET_BRANCH')
    github_token = os.environ.get('GITHUB_TOKEN')
    job_id = os.environ.get('JOB_ID')  

    # PR metadata
    pr_number = os.environ.get('PR_NUMBER')
    pr_title = os.environ.get('PR_TITLE')
    pr_author = os.environ.get('PR_AUTHOR')
    repo_full_name = os.environ.get('REPO_FULL_NAME')
    print(f"REPO FULL NAME: {repo_full_name}")

    # Get full git diff and commit IDs
    print("Generating full git diff...")
    full_diff = get_full_git_diff(source_branch, target_branch)
    if not full_diff:
        print("Warning: Full git diff is empty")
    
    print("Getting commit IDs...")
    commit_ids = get_commit_ids(source_branch, target_branch)
    if not commit_ids:
        print("Warning: Could not get commit IDs")

    # Base required parameters
    required_params = {
        'IMPACT_API_URL': impact_api_url,
        'API_ACCESS_TOKEN': api_access_token,
        'SOURCE_BRANCH': source_branch,
        'TARGET_BRANCH': target_branch,
        'REPO_FULL_NAME': repo_full_name,
        'GITHUB_TOKEN': github_token,
    }

    for param_name, param_value in required_params.items():
        if not param_value:
            print(f"Error: Missing required environment variable: {param_name}")
            sys.exit(1)

    if not full_diff:
        print("Error: Full git diff is empty")
        sys.exit(1)

    if not commit_ids:
        print("Error: Could not get commit IDs")
        sys.exit(1)

    # Construct payload matching ImpactRequest model
    payload = {
        # Required fields
        'repository': repo_full_name,
        'branch': source_branch,  
        'changes': full_diff,  
        'commit_ids': commit_ids,  
        'job_id': job_id,
        'github_token': github_token,

        # QAPI Integration (optional)
        'qapi_username': qapi_username,
        'qapi_password': qapi_password,
        'qapi_workspace_name': qapi_workspace_name,
        'qapi_suite_name': qapi_suite_name,
        'qapi_environment_name': qapi_environment_name,

        # Qyrus Integration (optional)
        'qyrus_api_token': qyrus_api_token,
        'team_name': team_name,

        # Web Integration (optional)
        'web_project_name': web_project_name,
        'web_suite_name': web_suite_name,
        'web_run_configuration_name': web_run_configuration_name,

        # Mobile Integration (optional)
        'mobile_project_name': mobile_project_name,
        'mobile_suite_name': mobile_suite_name,
        'mobile_run_configuration_name': mobile_run_configuration_name,

        # Desktop Integration (optional)
        'desktop_project_name': desktop_project_name,
        'desktop_suite_name': desktop_suite_name,
        'desktop_run_configuration_name': desktop_run_configuration_name,
    }

    # Remove None values from payload (optional fields that are None)
    payload = {k: v for k, v in payload.items() if v is not None}

    print("\n========= PAYLOAD DEBUG (JSON) =========")
    print(json.dumps(payload, indent=4))
    print("========================================\n")

    # Headers with custom access token
    headers = {
        'Content-Type': 'application/json',
        'X-API-Access-Token': api_access_token,
        'Authorization': f'Bearer {api_access_token}'
    }

    # Send request to Impact Analyzer API
    try:
        print(f"Sending impact analysis v3 request to {impact_api_url}")
        start_time = time.time()
        response = requests.post(
            impact_api_url,
            json=payload,
            headers=headers,
            timeout=30  # 30 seconds timeout
        )
        elapsed_time = time.time() - start_time

        print(
            f"Request completed in {elapsed_time:.2f}s with status code {response.status_code}"
        )

        if response.status_code in [200, 201, 202]:
            try:
                result = response.json()
                job_id = result.get('impact_analysis_id')
                print(
                    f"Impact analysis job created successfully. Job ID: {job_id}"
                )
                print(f"Response: {json.dumps(result, indent=2)}")

                with open('impact_analysis_job.txt', 'w') as f:
                    f.write(job_id)

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
