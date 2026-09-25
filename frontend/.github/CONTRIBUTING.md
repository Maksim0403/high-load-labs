# Contributing to the repository

To maintain a clean and navigable history, we follow strict standards for
branching, commits, and pull requests. Please ensure your contributions adhere
to the following guidelines.

## Branch Naming

All branch names must follow the [Conventional Branch](https://conventional-branch.github.io/)
specification and include the relevant Jira ticket ID.

**Format:**

`<type>/<jira-ticket>-<description>`

**Examples:**

- `feature/PT-1-add-authentication`
- `chore/PT-5-update-documentation-for-release`

## Commit Message Naming

All branch names must follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification and include the relevant Jira ticket ID.

**Format:**

`<type>[optional scope]: <jira-ticket> <description>`

**Examples:**

- `feat(auth): PT-1 add authentication using JWT tokens`
- `docs: PT-5 add release notes to the changelog`

## Pull Requests

### PR Titles

Pull request titles must follow the same style as commit titles:

`<type>[optional scope]: <jira-ticket> <description>`

**Examples:**

- `feat(auth): PT-1 add authentication with JWT tokens`
- `docs: PT-5 release notes for the v1.3.2 release`

### PR Description

Every repository includes a `PULL_REQUEST_TEMPLATE.md` in the .github folder.
This template will automatically populate the description field when you
open a new PR.

The "Additional information" section is optional and may be left blank if not
needed. Every other section of the template must be filled out before the PR
is created.
