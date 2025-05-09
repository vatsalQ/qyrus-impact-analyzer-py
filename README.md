


# Qyrus Impact Analyzer – GitHub Action

Generate a **structured diff** for every pull-request, post it to  **Qyrus Impact Analyzer** to check impact of the changes on your overall test repository.

![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Qyrus%20%20Impact%20Analyzer-neon)

---

## ✨ What it does

1. Verifies the scopes on the `GITHUB_TOKEN`
   • **fails** if it can’t read repo contents
   • **warns** if it can’t write Issues
2. `git diff`s PR **base ↔ head** and builds `structured_diff.json`
3. Captures PR metadata (number, title, author, repo)
4. Calls **Qyrus Impact-Analysis API**
5. Outputs the remote **`impact_analysis_id`**
6. *Optional* – opens a GitHub Issue that summarises the analysis when the token has `issues:write`

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
      - uses: your-org/code-impact-action@v1
        with:
          impact_api_url:   ${{ secrets.IMPACT_API_URL }}
          api_access_token: ${{ secrets.API_ACCESS_TOKEN }}
          project_id:       ${{ secrets.PROJECT_ID }}
```

Pin to `@v1` (major) or to a specific tag/SHA for reproducible builds.

---

## 🔑 Inputs

| name               | required | description                                                       |
| ------------------ | -------- | ----------------------------------------------------------------- |
| `impact_api_url`   | ✅        | Endpoint of your Impact-Analysis service (`https://…/analyze`)    |
| `api_access_token` | ✅        | Auth token (AI Token) expected by that service (`X-API-Access-Token` header) |
| `project_id`       | ✅        | Project identifier understood by the service                      |

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
| `PROJECT_ID`       | `34jfe-abce03-`                   |


## 📋 Troubleshooting

| symptom                                              | likely cause / fix                                     |
| ---------------------------------------------------- | ------------------------------------------------------ |
| `Token scopes: … (no contents)` → workflow **fails** | Add `permissions: contents: read`                      |
| `::warning::GITHUB_TOKEN lacks 'issues: write'`      | Issue creation skipped; add `issues: write` if desired |
| API call returns 401 / 403                           | Check `api_access_token`, CORS, or endpoint URL        |


