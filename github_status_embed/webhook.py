import json
import logging
import typing

import requests

from github_status_embed import types


log = logging.getLogger(__name__)

EMBED_DESCRIPTION = "GitHub Actions run [{run_id}]({run_url}) {status_verb}."
PULL_REQUEST_URL = "https://github.com/{repository}/pull/{number}"
ISSUE_URL = "https://github.com/{repository}/issues/{number}"
WEBHOOK_USERNAME = "GitHub Actions"
WEBHOOK_AVATAR_URL = (
    "https://raw.githubusercontent.com/"
    "893091483/Discord-embed/main/"
    "github_actions_avatar.png"
)
FIELD_CHARACTER_BUDGET = 60


def get_payload_pull_request(
        workflow: types.Workflow, pull_request: types.PullRequest
) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a Pull Request."""
    # Calculate the character budget for the Source Branch field
    author = pull_request.pr_author_login
    workflow_number = f"{workflow.name} #{workflow.number}"
    characters_left = FIELD_CHARACTER_BUDGET - len(author) - len(workflow_number)

    fields = [
        types.EmbedField(
            name="PR Author",
            value=f"[{author}]({pull_request.author_url})",
            inline=True,
        ),
        types.EmbedField(
            name="Workflow Run",
            value=f"[{workflow_number}]({workflow.url})",
            inline=True,
        ),
        types.EmbedField(
            name="Source Branch",
            value=pull_request.shortened_source(characters_left, owner=workflow.repository_owner),
            inline=True,
        ),
    ]

    embed = types.Embed(
        title=(
            f"[{workflow.repository}] Checks {workflow.status.adjective} on PR: "
            f"#{pull_request.number} {pull_request.title}"
        ),
        description=EMBED_DESCRIPTION.format(
            run_id=workflow.id, run_url=workflow.url, status_verb=workflow.status.verb,
        ),
        url=PULL_REQUEST_URL.format(
            repository=workflow.repository, number=pull_request.number
        ),
        color=workflow.status.color,
        fields=fields,
    )

    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[embed]
    )
    return webhook_payload

def get_payload_issue(
        workflow: types.Workflow, issue: types.Issue
) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a Pull Request."""
    # Calculate the character budget for the Source Branch field
    print"type(issue)"
    author = issue.issue_author_login
    workflow_number = f"{workflow.name} #{workflow.number}"
    status = issue.issue_status

    fields = [
        types.EmbedField(
            name="Issue Author",
            value=f"[{author}]({issue.author_url})",
            inline=True,
        ),
        types.EmbedField(
            name="Workflow Run",
            value=f"[{workflow_number}]({workflow.url})",
            inline=True,
        ),
        types.EmbedField(
            name="Issue Status ",
            value=f"[{status}]({workflow.url})",
            inline=True,
        ),
    ]

    embed = types.Embed(
        title=(
            f"[{workflow.repository}] Checks {workflow.status.adjective} on issue: "
            f"#{issue.number} {issue.title}"
        ),
        description=EMBED_DESCRIPTION.format(
            run_id=workflow.id, run_url=workflow.url, status_verb=workflow.status.verb,
        ),
        url=ISSUE_URL.format(
            repository=workflow.repository, number=issue.number
        ),
        color=workflow.status.color,
        fields=fields,
    )

    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[embed]
    )
    return webhook_payload

def get_payload(workflow: types.Workflow) -> types.WebhookPayload:
    """Create a WebhookPayload with information about a generic Workflow run."""
    embed_fields = [
        types.EmbedField(
            name="Actor",
            value=f"[{workflow.actor}]({workflow.actor_url})",
            inline=True,
        ),
        types.EmbedField(
            name="Workflow Run",
            value=f"[{workflow.name} #{workflow.number}]({workflow.url})",
            inline=True,
        ),
        types.EmbedField(
            name="Commit",
            value=f"[{workflow.short_sha}]({workflow.commit_url})",
            inline=True,
        ),
    ]

    embed = types.Embed(
        title=f"[{workflow.repository}] Workflow {workflow.status.adjective}",
        description=EMBED_DESCRIPTION.format(
            run_id=workflow.id, run_url=workflow.url, status_verb=workflow.status.verb,
        ),
        url=workflow.url,
        color=workflow.status.color,
        fields=embed_fields,
    )

    webhook_payload = types.WebhookPayload(
        username=WEBHOOK_USERNAME,
        avatar_url=WEBHOOK_AVATAR_URL,
        embeds=[embed]
    )

    return webhook_payload


def send_webhook(
        workflow: types.Workflow,
        webhook: types.Webhook,
        pull_request: typing.Optional[types.PullRequest],
        issue: typing.Optional[types.Issue],
        dry_run: bool = False,
) -> bool:
    """Send an embed to specified webhook."""
    if issue is not None:
        log.debug("Creating payload for Issue Check")
        payload = get_payload_issue(workflow, issue)
    elif pull_request is not None:
        log.debug("Creating payload for Pull Request Check")
        payload = get_payload_pull_request(workflow, pull_request)
    else:
        log.debug("Creating payload for non-Pull Request event")
        payload = get_payload(workflow)

    log.debug("Generated payload:\n%s", json.dumps(payload, indent=4))

    if dry_run:
        return True

    response = requests.post(webhook.url, json=payload)

    log.debug(f"Response: [{response.status_code}] {response.reason}")
    if response.ok:
        print(f"[status: {response.status_code}] Successfully delivered webhook payload!")
    else:
        # Output an error message using the GitHub Actions error command format
        print(
            "::error::Discord webhook delivery failed! "
            f"(status: {response.status_code}; reason: {response.reason})"
        )

    return response.ok
