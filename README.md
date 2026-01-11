# Qyrus Impact Analyzer – GitHub Action

Generates a **full git diff** for every pull-request and posts it to **Qyrus Impact Analyzer** to check the impact of changes on your overall test repository.

![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Qyrus%20%20Impact%20Analyzer-neon)

---

## ✨ What it does (v3)

1. Checks out the repository with full history
2. Generates a **full git diff** between the PR base and head branches
3. Extracts commit IDs (SHAs) for both branches
4. Captures PR metadata (number, title, author, repository)
5. Sends the diff, commit IDs, and metadata to **Qyrus Impact-Analysis API** with the new v3 payload format
6. Outputs the remote **`impact_analysis_id`** for tracking the analysis job

**Note:** v3 uses a simplified payload structure. The payload includes repository, branch, changes (full diff), commit IDs, and optional integration fields for QAPI, Qyrus, Web, Mobile, and Desktop platforms.

---

## 🚀 Quick start

```yaml
# .github/workflows/impact.yml
name: Code Impact Analysis
on:
  pull_request:
    branches: [main]

jobs:
  impact:
    runs-on: ubuntu-latest

    # ↓↓↓  REQUIRED SCOPES  ↓↓↓
    permissions:
      contents: read      # mandatory – lets the Action diff branches
      issues:   write     # optional – enables the “create Issue” step

    steps:
      - uses: your-org/code-impact-action@v3
        with:
          impact_api_url:    ${{ secrets.IMPACT_API_URL }}
          api_access_token:  ${{ secrets.API_ACCESS_TOKEN }}

          # Option 1: Use PROJECT_ID (optional if workspace is used)
          project_id:        ${{ secrets.PROJECT_ID }}

          # Option 2: Use workspace credentials instead of PROJECT_ID
          workspace_name:    ${{ secrets.WORKSPACE_NAME }}
          suite_name:        ${{ secrets.SUITE_NAME }}
          environment_name:  ${{ secrets.ENVIRONMENT_NAME }}
          username:          ${{ secrets.USERNAME }}
          password:          ${{ secrets.PASSWORD }}
```

Pin to `@v3` (major) or to a specific tag/SHA for reproducible builds.

### What's New in v3?

- **Full Git Diff**: Generates a complete git diff string instead of structured diff JSON
- **Simplified Payload**: New payload structure matching the `ImpactRequest` model
- **Commit IDs**: Includes commit SHAs for both source and target branches
- **Multiple Platform Support**: Optional fields for Web, Mobile, and Desktop test integrations
- **Qyrus Integration**: Direct support for Qyrus API token and team name
- **Backward Compatible**: Still supports QAPI workspace credentials (mapped to new field names)

---

## 🔑 Inputs

| name               | required | description                                                                 |
| ------------------ | -------- | --------------------------------------------------------------------------- |
| `impact_api_url`   | ✅        | Endpoint of your Impact-Analysis service (`https://…/analyze`)              |
| `api_access_token` | ✅        | Auth token expected by that service (`X-API-Access-Token` header)           |
| `github_token`     | ✅        | GitHub token with appropriate scopes (defaults to `${{ github.token }}`)    |
| `project_id`       | ❌        | Project identifier (optional if using workspace mode)                        |
| `workspace_name`   | ❌        | QAPI workspace name (required if `project_id` is not provided)             |
| `suite_name`       | ❌        | QAPI suite name (required if using workspace mode)                           |
| `environment_name` | ❌        | QAPI environment name (required if using workspace mode)                      |
| `username`         | ❌        | QAPI workspace username (required if using workspace mode)                   |
| `password`         | ❌        | QAPI workspace password (required if using workspace mode)                   |

**Note:** The action automatically generates the git diff and commit IDs from the PR branches. No additional configuration needed for these fields.

---


## 👮‍♂️ Required permissions

| scope            | why                                                   |
| ---------------- | ----------------------------------------------------- |
| `contents: read` | checkout & `git diff` across branches – **mandatory** |
| `issues: write`  | only if you want the Action to open a follow-up Issue |


If `contents:read` is missing, the Action stops immediately with
`::error::GITHUB_TOKEN is missing the 'contents' scope…`.

---

## 🛠 Secrets to set

| secret             | example value                        |
| ------------------ | ------------------------------------ |
| `IMPACT_API_URL`   | `https://stg-gateway.qyrus.com/impact-analyzer-py/` |
| `API_ACCESS_TOKEN` | `glpat-123456-abcdef`                |
| `PROJECT_ID`       | `34jfe-abce03-`                      |
| `WORKSPACE_NAME`   | `my_workspace`                        |
| `SUITE_NAME`       | `regression_suite`                     |
| `ENVIRONMENT_NAME` | `staging_env`                          |
| `USERNAME`         | `workspace_user`                       |
| `PASSWORD`         | `workspace_password`                   |



## 📋 Troubleshooting

| symptom                                              | likely cause / fix                                     |
| ---------------------------------------------------- | ------------------------------------------------------ |
| `Error: Full git diff is empty`                      | Ensure branches exist and have differences             |
| `Error: Could not get commit IDs`                    | Verify branch names are correct and accessible          |
| `Missing required environment variable`               | Check that all required inputs are provided            |
| API call returns 401 / 403                           | Check `api_access_token`, CORS, or endpoint URL        |
| API call returns 400                                 | Verify payload structure matches v3 `ImpactRequest` model |

## 📦 Payload Structure (v3)

The action sends a payload with the following structure:

```json
{
  "repository": "org/repo",
  "branch": "feature-branch",
  "changes": "full git diff string...",
  "commit_ids": "source_commit,target_commit",
  "job_id": "12345",
  "github_token": "...",
  "qapi_username": "...",
  "qapi_password": "...",
  "qapi_workspace_name": "...",
  "qapi_suite_name": "...",
  "qapi_environment_name": "..."
}
```



