---
short_description: Orchestrate SDK generation across multiple repositories
long_description: |
  Patterns for managing SDK generation when each language SDK lives in its own repository.
  Covers PR-triggered generation, cross-repo status reporting, PR reconciliation on merge/close,
  and main branch synchronization workflows.
source:
  repo: "customer-implementation"
  path: ".github/workflows/"
  ref: "main"
  last_reconciled: "2025-12-11"
---

# Multi-Repository SDK Workflows

When SDKs for different languages live in separate repositories (e.g., `myapi-typescript`, `myapi-python`, `myapi-go`), you need orchestration workflows to keep them synchronized with your OpenAPI specification.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     API Spec Repository                         │
│                    (openapi.yaml source)                        │
├─────────────────────────────────────────────────────────────────┤
│  PR opened/updated          │  PR merged/closed    │  Main push │
│         ↓                   │        ↓             │      ↓     │
│  kick-off-generation.yaml   │  reconcile-prs.yaml  │  sync.yaml │
└─────────────────────────────────────────────────────────────────┘
           │                           │                    │
           ▼                           ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ typescript-sdk   │  │ python-sdk       │  │ go-sdk           │
│ ├─ feature-branch│  │ ├─ feature-branch│  │ ├─ feature-branch│
│ └─ PR created    │  │ └─ PR created    │  │ └─ PR created    │
└──────────────────┘  └──────────────────┘  └──────────────────┘
```

## Workflow 1: Kick Off SDK Generation (PR Trigger)

This workflow triggers when a PR is opened or updated in the spec repository. It:
1. Runs `speakeasy run` to validate/transform the spec
2. Triggers SDK generation in each language repository
3. Reports status back to the source PR via comments

### Trigger Configuration

```yaml
name: Kick Off SDK Generation
permissions:
  checks: write
  contents: write
  pull-requests: write
  statuses: write
  id-token: write
  issues: write

on:
  pull_request:
    types: [opened, synchronize, reopened]
  workflow_dispatch:
```

### Job 1: Validate Spec and Prepare

```yaml
jobs:
  update_spec_and_generate_sdks:
    runs-on: ubuntu-latest
    steps:
      - name: Install Speakeasy CLI
        uses: mheap/setup-go-cli@fa9b01cdd4115eac636164f0de43bf7d51c82697
        with:
          owner: speakeasy-api
          repo: speakeasy
          cli_name: speakeasy
          package_type: zip

      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}
          ref: ${{ github.head_ref }}

      - name: Run Speakeasy workflow
        env:
          SPEAKEASY_API_KEY: ${{ secrets.SPEAKEASY_API_KEY }}
        run: speakeasy run
```

### Job 2: Trigger SDK Repos (Matrix Strategy)

```yaml
  trigger_sdk_workflows:
    needs: update_spec_and_generate_sdks
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - language: typescript
            owner: your-org
            repo: myapi-typescript
          - language: python
            owner: your-org
            repo: myapi-python
          - language: go
            owner: your-org
            repo: myapi-go
          - language: java
            owner: your-org
            repo: myapi-java
          - language: csharp
            owner: your-org
            repo: myapi-csharp
```

### Cross-Repo Workflow Dispatch

```yaml
    steps:
      - name: Prepare tag name
        id: tag
        run: echo "name=$(echo "${{ github.head_ref }}" | sed 's|/|-|g')" >> $GITHUB_OUTPUT

      - name: Trigger SDK generation
        env:
          GH_TOKEN: ${{ secrets.SDK_REPOS_PAT }}  # PAT with repo access to SDK repos
        run: |
          owner="${{ matrix.owner }}"
          repo="${{ matrix.repo }}"
          branch="${{ github.head_ref }}"
          tag_name="${{ steps.tag.outputs.name }}"

          # Trigger the SDK repo's generation workflow
          gh workflow run sdk_generation.yaml \
            --repo "$owner/$repo" \
            --ref main \
            --field feature_branch="$branch" \
            --field environment="tag=$tag_name"

          # Wait for workflow to register
          sleep 10

          # Capture run ID for status tracking
          run_id=$(gh run list \
            --repo "$owner/$repo" \
            --workflow sdk_generation.yaml \
            --limit 1 \
            --json databaseId \
            --jq '.[0].databaseId')

          echo "WORKFLOW_RUN_ID=$run_id" >> $GITHUB_ENV
```

### PR Comment Status Reporting

Report SDK generation status back to the source PR:

```yaml
      - name: Note pending status on PR
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          language="${{ matrix.language }}"
          repo="${{ matrix.repo }}"
          owner="${{ matrix.owner }}"
          marker="<!-- sdk-${language}-status -->"

          comment_body="$marker
### ${language} SDK generation

| Repository | Workflow Run | Status | SDK PR |
| --- | --- | --- | --- |
| [$repo](https://github.com/$owner/$repo) | Pending | ⏳ In Progress | Pending |"

          # Find existing comment or create new one
          comments_json=$(gh api \
            "repos/${{ github.repository }}/issues/${{ github.event.pull_request.number }}/comments?per_page=100")

          existing_id=$(echo "$comments_json" | \
            jq -r --arg marker "$marker" \
            'map(select(.body | contains($marker))) | last | .id // empty')

          if [[ -n "$existing_id" ]]; then
            gh api --method PATCH \
              "repos/${{ github.repository }}/issues/comments/$existing_id" \
              -f body="$comment_body"
          else
            gh api --method POST \
              "repos/${{ github.repository }}/issues/${{ github.event.pull_request.number }}/comments" \
              -f body="$comment_body"
          fi
```

### Poll and Update Final Status

```yaml
      - name: Wait for SDK workflow completion
        env:
          GH_TOKEN: ${{ secrets.SDK_REPOS_PAT }}
        run: |
          owner="${{ matrix.owner }}"
          repo="${{ matrix.repo }}"
          run_id="$WORKFLOW_RUN_ID"

          while true; do
            resp=$(gh api "repos/$owner/$repo/actions/runs/$run_id")
            status=$(echo "$resp" | jq -r '.status')
            conclusion=$(echo "$resp" | jq -r '.conclusion')

            if [[ "$status" == "completed" ]]; then
              if [[ "$conclusion" == "success" ]]; then
                echo "WORKFLOW_SUCCESS=true" >> $GITHUB_ENV
              else
                echo "WORKFLOW_SUCCESS=false" >> $GITHUB_ENV
              fi
              break
            fi
            sleep 30
          done

      - name: Update PR comment with result
        if: always()
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          SDK_PAT: ${{ secrets.SDK_REPOS_PAT }}
        run: |
          language="${{ matrix.language }}"
          repo="${{ matrix.repo }}"
          owner="${{ matrix.owner }}"
          branch="${{ github.head_ref }}"
          marker="<!-- sdk-${language}-status -->"

          # Find SDK PR if created
          pr_url=$(GH_TOKEN="$SDK_PAT" gh pr list \
            --repo "$owner/$repo" \
            --head "$branch" \
            --json url \
            --jq '.[0].url' 2>/dev/null || echo "")

          if [[ "$WORKFLOW_SUCCESS" == "true" ]]; then
            status_cell="✅ Success"
          else
            status_cell="❌ Failed"
          fi

          run_url="https://github.com/$owner/$repo/actions/runs/$WORKFLOW_RUN_ID"

          if [[ -n "$pr_url" && "$pr_url" != "null" ]]; then
            pr_cell="[SDK PR]($pr_url)"
          else
            pr_cell="[Compare branch](https://github.com/$owner/$repo/compare/main...$branch)"
          fi

          comment_body="$marker
### ${language} SDK generation

| Repository | Workflow Run | Status | SDK PR |
| --- | --- | --- | --- |
| [$repo](https://github.com/$owner/$repo) | [View run]($run_url) | $status_cell | $pr_cell |"

          # Update comment
          comments_json=$(gh api \
            "repos/${{ github.repository }}/issues/${{ github.event.pull_request.number }}/comments?per_page=100")
          comment_id=$(echo "$comments_json" | \
            jq -r --arg marker "$marker" \
            'map(select(.body | contains($marker))) | last | .id // empty')

          gh api --method PATCH \
            "repos/${{ github.repository }}/issues/comments/$comment_id" \
            -f body="$comment_body"

          # Fail job if SDK generation failed
          [[ "$WORKFLOW_SUCCESS" == "true" ]] || exit 1
```

---

## Workflow 2: Reconcile SDK PRs (On Merge/Close)

When the source PR is merged or closed, automatically merge or close the corresponding SDK PRs:

```yaml
name: Reconcile SDK PRs
permissions:
  contents: read
  pull-requests: read

on:
  pull_request:
    types: [closed]

jobs:
  manage_sdk_prs:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        include:
          - language: typescript
            owner: your-org
            repo: myapi-typescript
          - language: python
            owner: your-org
            repo: myapi-python
          - language: go
            owner: your-org
            repo: myapi-go
          - language: java
            owner: your-org
            repo: myapi-java
          - language: csharp
            owner: your-org
            repo: myapi-csharp

    steps:
      - name: Manage ${{ matrix.language }} SDK PR
        env:
          GH_TOKEN: ${{ secrets.SDK_REPOS_PAT }}
        run: |
          branch_name="${{ github.event.pull_request.head.ref }}"
          repo="${{ matrix.repo }}"
          owner="${{ matrix.owner }}"
          was_merged="${{ github.event.pull_request.merged }}"

          echo "Looking for PR in $owner/$repo with branch: $branch_name"
          echo "Source PR was merged: $was_merged"

          # Find PR with matching branch name
          pr_data=$(gh pr list \
            --repo "$owner/$repo" \
            --head "$branch_name" \
            --json number,title,url \
            --jq '.[0]' 2>/dev/null || echo "null")

          if [[ "$pr_data" != "null" && -n "$pr_data" ]]; then
            pr_number=$(echo "$pr_data" | jq -r '.number')
            pr_title=$(echo "$pr_data" | jq -r '.title')
            pr_url=$(echo "$pr_data" | jq -r '.url')

            if [[ "$was_merged" == "true" ]]; then
              echo "Merging SDK PR #$pr_number..."
              gh pr merge "$pr_number" \
                --repo "$owner/$repo" \
                --squash \
                --delete-branch
              echo "✅ Merged: $pr_title"
            else
              echo "Closing SDK PR #$pr_number..."
              gh pr close "$pr_number" \
                --repo "$owner/$repo" \
                --comment "Closing SDK PR because the source PR was closed without merging."
              echo "✅ Closed: $pr_title"
            fi
          else
            echo "No PR found in $repo for branch $branch_name"
          fi
```

---

## Workflow 3: Main Branch Sync

Simple workflow for direct pushes to main (e.g., after PR merge):

```yaml
name: Speakeasy Main Sync
permissions:
  checks: write
  contents: write
  pull-requests: write
  statuses: write
  id-token: write

on:
  push:
    branches:
      - main

jobs:
  run_speakeasy_workflow:
    runs-on: ubuntu-latest
    steps:
      - name: Install Speakeasy CLI
        uses: mheap/setup-go-cli@fa9b01cdd4115eac636164f0de43bf7d51c82697
        with:
          owner: speakeasy-api
          repo: speakeasy
          cli_name: speakeasy
          package_type: zip

      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          token: ${{ secrets.GITHUB_TOKEN }}

      - name: Run Speakeasy workflow
        env:
          SPEAKEASY_API_KEY: ${{ secrets.SPEAKEASY_API_KEY }}
        run: speakeasy run
```

---

## SDK Repository Workflow

Each SDK repository needs a workflow that can be triggered remotely:

```yaml
# .github/workflows/sdk_generation.yaml (in each SDK repo)
name: SDK Generation

on:
  workflow_dispatch:
    inputs:
      feature_branch:
        description: 'Feature branch name from source repo'
        required: false
      environment:
        description: 'Environment variables (key=value format)'
        required: false

jobs:
  generate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: main

      - name: Create feature branch
        if: inputs.feature_branch != ''
        run: |
          git checkout -b "${{ inputs.feature_branch }}" || \
          git checkout "${{ inputs.feature_branch }}"

      - name: Install Speakeasy CLI
        uses: speakeasy-api/speakeasy-action@v1
        with:
          speakeasy_api_key: ${{ secrets.SPEAKEASY_API_KEY }}

      - name: Generate SDK
        run: speakeasy run -y

      - name: Create PR
        if: inputs.feature_branch != ''
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          git add -A
          git commit -m "chore: regenerate SDK from ${{ inputs.feature_branch }}" || exit 0

          git push -u origin "${{ inputs.feature_branch }}"

          gh pr create \
            --title "SDK update from ${{ inputs.feature_branch }}" \
            --body "Automated SDK regeneration triggered by spec changes." \
            --base main \
            --head "${{ inputs.feature_branch }}" || echo "PR already exists"
```

---

## Required Secrets

| Secret | Scope | Purpose |
|--------|-------|---------|
| `SPEAKEASY_API_KEY` | All repos | Speakeasy CLI authentication |
| `SDK_REPOS_PAT` | Spec repo | Personal Access Token with `repo` scope for all SDK repos |
| `GITHUB_TOKEN` | Auto | Default token for same-repo operations |

### Creating the PAT

1. Go to GitHub Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Create token with:
   - Repository access: Select all SDK repositories
   - Permissions:
     - Contents: Read and write
     - Pull requests: Read and write
     - Actions: Read and write (for workflow dispatch)
3. Add as `SDK_REPOS_PAT` secret in spec repository

---

## PR Comment Format

The status comments use HTML markers for idempotent updates:

```markdown
<!-- sdk-typescript-status -->
### typescript SDK generation

| Repository | Workflow Run | Status | SDK PR |
| --- | --- | --- | --- |
| [myapi-typescript](https://github.com/org/myapi-typescript) | [View run](url) | ✅ Success | [SDK PR](url) |
```

Each language gets its own comment with a unique marker, allowing parallel updates without conflicts.

---

## Pre-defined TODO List

When implementing multi-repo SDK workflows:

| Step | TODO Item | Active Form |
|------|-----------|-------------|
| 1 | Create SDK repositories for each language | Creating SDK repositories |
| 2 | Configure sdk_generation.yaml in each SDK repo | Configuring SDK generation workflows |
| 3 | Create PAT with access to all SDK repos | Creating cross-repo PAT |
| 4 | Add PAT as secret in spec repository | Adding PAT secret |
| 5 | Create kick-off-generation.yaml workflow | Creating kick-off workflow |
| 6 | Create reconcile-prs.yaml workflow | Creating reconciliation workflow |
| 7 | Create main sync workflow | Creating main sync workflow |
| 8 | Test PR flow end-to-end | Testing PR flow |
| 9 | Test merge reconciliation | Testing merge reconciliation |

**Usage:**
```
TodoWrite([
  {content: "Create SDK repositories for each language", status: "pending", activeForm: "Creating SDK repositories"},
  {content: "Configure sdk_generation.yaml in each SDK repo", status: "pending", activeForm: "Configuring SDK generation workflows"},
  {content: "Create PAT with access to all SDK repos", status: "pending", activeForm: "Creating cross-repo PAT"},
  {content: "Add PAT as secret in spec repository", status: "pending", activeForm: "Adding PAT secret"},
  {content: "Create kick-off-generation.yaml workflow", status: "pending", activeForm: "Creating kick-off workflow"},
  {content: "Create reconcile-prs.yaml workflow", status: "pending", activeForm: "Creating reconciliation workflow"},
  {content: "Create main sync workflow", status: "pending", activeForm: "Creating main sync workflow"},
  {content: "Test PR flow end-to-end", status: "pending", activeForm: "Testing PR flow"},
  {content: "Test merge reconciliation", status: "pending", activeForm: "Testing merge reconciliation"}
])
```

---

## Comparison: Multi-Repo vs Monorepo

| Aspect | Multi-Repo | Monorepo |
|--------|-----------|----------|
| **Isolation** | Each SDK has independent versioning | Shared versioning possible |
| **CI Complexity** | Higher (cross-repo orchestration) | Lower (single workflow) |
| **Access Control** | Per-language repo permissions | Single repo permissions |
| **Release Flexibility** | Independent release schedules | Coordinated releases |
| **Best For** | Large teams, different SDK maintainers | Small teams, unified releases |

Multi-repo is preferred when:
- Different teams maintain different SDKs
- SDKs have different release cadences
- You want language-specific CI/CD configurations
- Users should only see one language's issues/PRs
