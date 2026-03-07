#!/usr/bin/env python3

import os
import sys
import json
import requests
import time


def _parse_bool(value):
    if value is None:
        return False
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _redact_sensitive(payload):
    """Return a copy safe for logs (secrets masked)."""
    redacted = json.loads(json.dumps(payload))
    sensitive_keys = {"api_access_token", "password", "api_token", "github_token"}
    for key in sensitive_keys:
        if key in redacted and redacted[key]:
            redacted[key] = "***REDACTED***"
    if redacted.get("business_context", {}).get("connector_config", {}).get("api_token"):
        redacted["business_context"]["connector_config"]["api_token"] = "***REDACTED***"
    return redacted


def main():
    # Get environment variables
    impact_api_url = os.environ.get('IMPACT_API_URL')
    api_access_token = os.environ.get('API_ACCESS_TOKEN')
    project_id = os.environ.get('PROJECT_ID')

    # New optional/required envs
    workspace_name = os.environ.get('WORKSPACE_NAME')
    suite_name = os.environ.get('SUITE_NAME')
    environment_name = os.environ.get('ENVIRONMENT_NAME')
    username = os.environ.get('USERNAME', '')
    password = os.environ.get('PASSWORD', '')
    api_token = os.environ.get('QAPI_API_TOKEN', '')
    business_docs_enabled = _parse_bool(os.environ.get('BUSINESS_DOCS_ENABLED', 'false'))
    business_docs_source = os.environ.get('BUSINESS_DOCS_SOURCE', 'confluence')
    business_doc_refs_raw = os.environ.get('BUSINESS_DOC_REFS', '')
    business_docs_mode = os.environ.get('BUSINESS_DOCS_MODE', 'semantic_validation')
    confluence_base_url = os.environ.get('CONFLUENCE_BASE_URL', '')
    confluence_username = os.environ.get('CONFLUENCE_USERNAME', '')
    confluence_api_token = os.environ.get('CONFLUENCE_API_TOKEN', '')
    confluence_output_format = os.environ.get('CONFLUENCE_OUTPUT_FORMAT', 'markdown')

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
        
        
    # Base required parameters
    required_params = {
        'IMPACT_API_URL': impact_api_url,
        'API_ACCESS_TOKEN': api_access_token,
        'SOURCE_BRANCH': source_branch,
        'TARGET_BRANCH': target_branch,
    }

    for param_name, param_value in required_params.items():
        if not param_value:
            print(f"Error: Missing required environment variable: {param_name}")
            sys.exit(1)

  
    if not project_id and not workspace_name:
        print("Error: Must provide either PROJECT_ID or WORKSPACE_NAME")
        sys.exit(1)

    if workspace_name:
        workspace_required = {
            'WORKSPACE_NAME': workspace_name,
            'SUITE_NAME': suite_name,
            'ENVIRONMENT_NAME': environment_name,
            'USERNAME': username,
            # 'PASSWORD': password
        }
        for param_name, param_value in workspace_required.items():
            if not param_value:
                print(f"Error: Missing required workspace environment variable: {param_name}")
                sys.exit(1)
        
        if not api_token and not password:
            print("Error: Must provide either QAPI_API_TOKEN or PASSWORD")
            sys.exit(1)


    if not structured_diff or not structured_diff.get('files'):
        print("Error: Structured diff is empty or invalid")
        sys.exit(1)

    business_context = None
    if business_docs_enabled:
        if business_docs_mode not in ('reference_only', 'semantic_validation'):
            print("Error: BUSINESS_DOCS_MODE must be reference_only or semantic_validation")
            sys.exit(1)

        documents = []
        if business_doc_refs_raw:
            try:
                documents = json.loads(business_doc_refs_raw)
            except json.JSONDecodeError:
                print("Error: BUSINESS_DOC_REFS must be a valid JSON array")
                sys.exit(1)
            if not isinstance(documents, list):
                print("Error: BUSINESS_DOC_REFS must be a JSON array")
                sys.exit(1)

        business_context = {
            "enabled": True,
            "source": business_docs_source,
            "mode": business_docs_mode,
            "documents": documents,
        }

        if business_docs_source == "confluence":
            missing_confluence = []
            if not confluence_base_url:
                missing_confluence.append("CONFLUENCE_BASE_URL")
            if not confluence_username:
                missing_confluence.append("CONFLUENCE_USERNAME")
            if not confluence_api_token:
                missing_confluence.append("CONFLUENCE_API_TOKEN")
            if missing_confluence:
                print(
                    "Error: Missing required Confluence environment variables: "
                    + ", ".join(missing_confluence)
                )
                sys.exit(1)
            business_context["connector_config"] = {
                "base_url": confluence_base_url,
                "username": confluence_username,
                "api_token": confluence_api_token,
                "output_format": confluence_output_format,
            }

    # Construct payload with all environment variables included
    payload = {
        'project_id': project_id if project_id else None,
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
        'repo_url': repo_url,
        'workspace_name': workspace_name,
        'suite_name': suite_name,
        'environment_name': environment_name,
        'api_access_token': api_access_token,
        'username': username,
        'password': password,
        "api_token": api_token
    }
    if business_context:
        payload["business_context"] = business_context

    print("\n========= PAYLOAD DEBUG (JSON) =========")
    print(json.dumps(_redact_sensitive(payload), indent=4))
    print("========================================\n")

    # Headers with custom access token
    headers = {
        'Content-Type': 'application/json',
        'X-API-Access-Token': api_access_token,
        'Authorization': f'Bearer {api_access_token}'
    }

    # Send request to Impact Analyzer API
    try:
        print(f"Sending impact analysis v2 request to {impact_api_url}")
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
