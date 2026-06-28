import base64
import json
import os
import subprocess
from dataclasses import dataclass
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv()


class IntegrationError(RuntimeError):
    pass


@dataclass(frozen=True)
class IntegrationDefinition:
    name: str
    required_env: tuple[str, ...]
    actions: tuple[str, ...]


INTEGRATIONS = {
    "github": IntegrationDefinition(
        name="GitHub",
        required_env=("GITHUB_TOKEN",),
        actions=("status", "list_repos", "list_issues", "create_issue"),
    ),
    "gmail": IntegrationDefinition(
        name="Gmail",
        required_env=("GOOGLE_ACCESS_TOKEN",),
        actions=("status", "list_messages", "send_email"),
    ),
    "google_drive": IntegrationDefinition(
        name="Google Drive",
        required_env=("GOOGLE_ACCESS_TOKEN",),
        actions=("status", "list_files"),
    ),
    "slack": IntegrationDefinition(
        name="Slack",
        required_env=("SLACK_BOT_TOKEN",),
        actions=("status", "list_channels", "send_message"),
    ),
    "notion": IntegrationDefinition(
        name="Notion",
        required_env=("NOTION_TOKEN",),
        actions=("status", "search", "create_page"),
    ),
    "linear": IntegrationDefinition(
        name="Linear",
        required_env=("LINEAR_API_KEY",),
        actions=("status", "list_issues", "create_issue"),
    ),
    "jira": IntegrationDefinition(
        name="Jira",
        required_env=("JIRA_SITE_URL", "JIRA_EMAIL", "JIRA_API_TOKEN"),
        actions=("status", "list_projects", "create_issue"),
    ),
    "discord": IntegrationDefinition(
        name="Discord",
        required_env=("DISCORD_BOT_TOKEN",),
        actions=("status", "list_guilds", "send_message"),
    ),
    "docker": IntegrationDefinition(
        name="Docker",
        required_env=(),
        actions=("status", "list_containers", "list_images"),
    ),
    "mongodb": IntegrationDefinition(
        name="MongoDB",
        required_env=("MONGODB_URI",),
        actions=("status", "list_databases", "list_collections"),
    ),
}


class IntegrationManager:
    def list_services(self):
        return [
            {
                "key": key,
                "name": definition.name,
                "configured": self.is_configured(key),
                "missing_env": self.missing_env(key),
                "required_env": list(definition.required_env),
                "actions": list(definition.actions),
            }
            for key, definition in INTEGRATIONS.items()
        ]

    def is_configured(self, service: str):
        return not self.missing_env(service)

    def missing_env(self, service: str):
        definition = self._definition(service)
        return [name for name in definition.required_env if not os.getenv(name)]

    def execute(self, service: str, action: str = "status", **kwargs):
        service = self._normalize_service(service)
        action = action or "status"

        handler_name = f"_{service}_{action}"
        handler = getattr(self, handler_name, None)
        if handler is None:
            definition = self._definition(service)
            raise IntegrationError(
                f"Unsupported action '{action}' for {definition.name}. "
                f"Available actions: {', '.join(definition.actions)}"
            )

        if service != "docker":
            self._require_config(service)

        return handler(**kwargs)

    def _definition(self, service: str):
        service = self._normalize_service(service)
        if service not in INTEGRATIONS:
            raise IntegrationError(f"Unknown integration: {service}")
        return INTEGRATIONS[service]

    def _normalize_service(self, service: str):
        key = (service or "").strip().lower().replace(" ", "_").replace("-", "_")
        aliases = {
            "drive": "google_drive",
            "google": "google_drive",
            "google_drive": "google_drive",
            "mongo": "mongodb",
        }
        return aliases.get(key, key)

    def _require_config(self, service: str):
        missing = self.missing_env(service)
        if missing:
            definition = self._definition(service)
            raise IntegrationError(
                f"{definition.name} is not configured. Add these values to .env: "
                f"{', '.join(missing)}"
            )

    def _request(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        auth=None,
    ):
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json_body,
            auth=auth,
            timeout=60,
        )

        if response.status_code >= 400:
            body = response.text[:1000]
            raise IntegrationError(f"{method} {url} failed: {response.status_code} {body}")

        if not response.text:
            return {}

        try:
            return response.json()
        except ValueError:
            return {"text": response.text}

    def _run_command(self, command: list[str]):
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode != 0:
            raise IntegrationError(result.stderr.strip() or f"{command[0]} failed")
        return result.stdout.strip()

    # GitHub
    def _github_headers(self):
        return {
            "Authorization": f"Bearer {os.getenv('GITHUB_TOKEN')}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    def _github_status(self):
        user = self._request("GET", "https://api.github.com/user", headers=self._github_headers())
        return {"connected": True, "login": user.get("login"), "id": user.get("id")}

    def _github_list_repos(self, limit=20):
        repos = self._request(
            "GET",
            "https://api.github.com/user/repos",
            headers=self._github_headers(),
            params={"per_page": min(int(limit), 100), "sort": "updated"},
        )
        return [
            {
                "full_name": repo.get("full_name"),
                "private": repo.get("private"),
                "updated_at": repo.get("updated_at"),
                "html_url": repo.get("html_url"),
            }
            for repo in repos
        ]

    def _github_list_issues(self, repo, state="open", limit=20):
        return self._request(
            "GET",
            f"https://api.github.com/repos/{repo}/issues",
            headers=self._github_headers(),
            params={"state": state, "per_page": min(int(limit), 100)},
        )

    def _github_create_issue(self, repo, title, body=""):
        return self._request(
            "POST",
            f"https://api.github.com/repos/{repo}/issues",
            headers=self._github_headers(),
            json_body={"title": title, "body": body},
        )

    # Gmail / Google Drive
    def _google_headers(self):
        return {"Authorization": f"Bearer {os.getenv('GOOGLE_ACCESS_TOKEN')}"}

    def _gmail_status(self):
        profile = self._request(
            "GET",
            "https://gmail.googleapis.com/gmail/v1/users/me/profile",
            headers=self._google_headers(),
        )
        return {"connected": True, **profile}

    def _gmail_list_messages(self, query="", limit=10):
        return self._request(
            "GET",
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers=self._google_headers(),
            params={"q": query, "maxResults": min(int(limit), 100)},
        )

    def _gmail_send_email(self, to, subject, body):
        raw_message = f"To: {to}\r\nSubject: {subject}\r\n\r\n{body}"
        encoded = base64.urlsafe_b64encode(raw_message.encode("utf-8")).decode("utf-8")
        return self._request(
            "POST",
            "https://gmail.googleapis.com/gmail/v1/users/me/messages/send",
            headers=self._google_headers(),
            json_body={"raw": encoded},
        )

    def _google_drive_status(self):
        about = self._request(
            "GET",
            "https://www.googleapis.com/drive/v3/about",
            headers=self._google_headers(),
            params={"fields": "user,storageQuota"},
        )
        return {"connected": True, **about}

    def _google_drive_list_files(self, query="", limit=20):
        return self._request(
            "GET",
            "https://www.googleapis.com/drive/v3/files",
            headers=self._google_headers(),
            params={
                "q": query or None,
                "pageSize": min(int(limit), 100),
                "fields": "files(id,name,mimeType,modifiedTime,webViewLink)",
            },
        )

    # Slack
    def _slack_headers(self):
        return {"Authorization": f"Bearer {os.getenv('SLACK_BOT_TOKEN')}"}

    def _slack_request(self, method, url, **kwargs):
        data = self._request(method, url, headers=self._slack_headers(), **kwargs)
        if data.get("ok") is False:
            raise IntegrationError(f"Slack API error: {data.get('error')}")
        return data

    def _slack_status(self):
        return self._slack_request("GET", "https://slack.com/api/auth.test")

    def _slack_list_channels(self, limit=100):
        return self._slack_request(
            "GET",
            "https://slack.com/api/conversations.list",
            params={"limit": min(int(limit), 1000)},
        )

    def _slack_send_message(self, channel, text):
        return self._slack_request(
            "POST",
            "https://slack.com/api/chat.postMessage",
            json_body={"channel": channel, "text": text},
        )

    # Notion
    def _notion_headers(self):
        return {
            "Authorization": f"Bearer {os.getenv('NOTION_TOKEN')}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json",
        }

    def _notion_status(self):
        return self._request("GET", "https://api.notion.com/v1/users/me", headers=self._notion_headers())

    def _notion_search(self, query="", limit=10):
        return self._request(
            "POST",
            "https://api.notion.com/v1/search",
            headers=self._notion_headers(),
            json_body={"query": query, "page_size": min(int(limit), 100)},
        )

    def _notion_create_page(self, parent_page_id, title, content=""):
        children = []
        if content:
            children.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {"rich_text": [{"type": "text", "text": {"content": content}}]},
            })
        return self._request(
            "POST",
            "https://api.notion.com/v1/pages",
            headers=self._notion_headers(),
            json_body={
                "parent": {"page_id": parent_page_id},
                "properties": {
                    "title": {
                        "title": [{"type": "text", "text": {"content": title}}],
                    }
                },
                "children": children,
            },
        )

    # Linear
    def _linear_headers(self):
        return {
            "Authorization": os.getenv("LINEAR_API_KEY"),
            "Content-Type": "application/json",
        }

    def _linear_graphql(self, query, variables=None):
        data = self._request(
            "POST",
            "https://api.linear.app/graphql",
            headers=self._linear_headers(),
            json_body={"query": query, "variables": variables or {}},
        )
        if data.get("errors"):
            raise IntegrationError(json.dumps(data["errors"], indent=2))
        return data.get("data", data)

    def _linear_status(self):
        return self._linear_graphql("query { viewer { id name email } }")

    def _linear_list_issues(self, limit=20):
        return self._linear_graphql(
            """
            query($limit: Int!) {
              issues(first: $limit, orderBy: updatedAt) {
                nodes { id identifier title state { name } assignee { name } url }
              }
            }
            """,
            {"limit": min(int(limit), 100)},
        )

    def _linear_create_issue(self, team_id, title, description=""):
        return self._linear_graphql(
            """
            mutation($input: IssueCreateInput!) {
              issueCreate(input: $input) {
                success
                issue { id identifier title url }
              }
            }
            """,
            {"input": {"teamId": team_id, "title": title, "description": description}},
        )

    # Jira
    def _jira_base_url(self):
        return os.getenv("JIRA_SITE_URL", "").rstrip("/")

    def _jira_auth(self):
        return (os.getenv("JIRA_EMAIL"), os.getenv("JIRA_API_TOKEN"))

    def _jira_status(self):
        return self._request(
            "GET",
            f"{self._jira_base_url()}/rest/api/3/myself",
            auth=self._jira_auth(),
        )

    def _jira_list_projects(self):
        return self._request(
            "GET",
            f"{self._jira_base_url()}/rest/api/3/project/search",
            auth=self._jira_auth(),
        )

    def _jira_create_issue(self, project_key, issue_type, summary, description=""):
        return self._request(
            "POST",
            f"{self._jira_base_url()}/rest/api/3/issue",
            auth=self._jira_auth(),
            json_body={
                "fields": {
                    "project": {"key": project_key},
                    "issuetype": {"name": issue_type},
                    "summary": summary,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}],
                        }],
                    },
                }
            },
        )

    # Discord
    def _discord_headers(self):
        return {"Authorization": f"Bot {os.getenv('DISCORD_BOT_TOKEN')}"}

    def _discord_status(self):
        return self._request("GET", "https://discord.com/api/v10/users/@me", headers=self._discord_headers())

    def _discord_list_guilds(self):
        return self._request("GET", "https://discord.com/api/v10/users/@me/guilds", headers=self._discord_headers())

    def _discord_send_message(self, channel_id, content):
        return self._request(
            "POST",
            f"https://discord.com/api/v10/channels/{channel_id}/messages",
            headers=self._discord_headers(),
            json_body={"content": content},
        )

    # Docker
    def _docker_status(self):
        return {"connected": True, "version": self._run_command(["docker", "--version"])}

    def _docker_list_containers(self):
        output = self._run_command(["docker", "ps", "--format", "json"])
        return [json.loads(line) for line in output.splitlines() if line.strip()]

    def _docker_list_images(self):
        output = self._run_command(["docker", "images", "--format", "json"])
        return [json.loads(line) for line in output.splitlines() if line.strip()]

    # MongoDB
    def _mongodb_client(self):
        try:
            from pymongo import MongoClient
        except ImportError as exc:
            raise IntegrationError("Install pymongo to use MongoDB: pip install pymongo") from exc

        return MongoClient(os.getenv("MONGODB_URI"), serverSelectionTimeoutMS=5000)

    def _mongodb_status(self):
        with self._mongodb_client() as client:
            return client.admin.command("ping")

    def _mongodb_list_databases(self):
        with self._mongodb_client() as client:
            return client.list_database_names()

    def _mongodb_list_collections(self, database):
        with self._mongodb_client() as client:
            return client[database].list_collection_names()
