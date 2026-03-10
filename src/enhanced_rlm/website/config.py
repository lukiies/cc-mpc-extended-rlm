"""Website configuration loaded from project .env file."""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class WebsiteUser:
    """A user for client-side authentication."""
    id: str
    email: str
    name: str
    role: str  # "admin" or "user"
    password: str


@dataclass
class WebsiteConfig:
    """Configuration for the documentation website."""
    enabled: bool = False
    prefix: str = ""           # e.g. "rdm" → rdm.domain.com
    domain: str = ""           # e.g. "robak.net.pl"
    title: str = "Knowledge Base"
    subtitle: str = "Project Documentation"
    deploy_host: str = ""      # SSH alias or hostname
    deploy_path: str = ""      # Remote path for index.html
    users: list[WebsiteUser] = field(default_factory=list)

    @property
    def full_domain(self) -> str:
        """Get full website domain: prefix.domain."""
        if self.prefix and self.domain:
            return f"{self.prefix}.{self.domain}"
        return self.domain or self.prefix

    @property
    def url(self) -> str:
        """Get full website URL."""
        domain = self.full_domain
        return f"https://{domain}" if domain else ""


def _parse_users(users_str: str) -> list[WebsiteUser]:
    """Parse WEBSITE_USERS env var into WebsiteUser objects.

    Format: email:password:name:role (comma-separated for multiple users)
    Example: admin@example.com:pass123:Admin User:admin,user@example.com:pass456:Regular User:user
    """
    if not users_str or not users_str.strip():
        return []

    users = []
    for i, entry in enumerate(users_str.split(","), start=1):
        entry = entry.strip()
        if not entry:
            continue
        parts = entry.split(":")
        if len(parts) < 4:
            continue
        users.append(WebsiteUser(
            id=str(i),
            email=parts[0].strip(),
            password=parts[1].strip(),
            name=parts[2].strip(),
            role=parts[3].strip(),
        ))
    return users


def load_website_config(workspace_path: Path) -> WebsiteConfig:
    """Load website configuration from the project's .env file.

    Args:
        workspace_path: Path to the project workspace root.

    Returns:
        WebsiteConfig with values from .env, or defaults if .env not found.
    """
    env_path = workspace_path / ".env"
    env_vars: dict[str, str] = {}

    if env_path.exists():
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()
                # Remove surrounding quotes if present
                if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                    value = value[1:-1]
                env_vars[key] = value

    enabled_str = env_vars.get("WEBSITE_ENABLED", "false").lower()
    enabled = enabled_str in ("true", "1", "yes")

    prefix = env_vars.get("WEBSITE_PREFIX", "")
    domain = env_vars.get("WEBSITE_DOMAIN", "")
    deploy_host = env_vars.get("WEBSITE_DEPLOY_HOST", "")

    # Support {prefix} and {domain} placeholders in deploy path
    deploy_path = env_vars.get("WEBSITE_DEPLOY_PATH", "")
    if deploy_path:
        deploy_path = deploy_path.replace("{prefix}", prefix)
        deploy_path = deploy_path.replace("{domain}", domain)

    return WebsiteConfig(
        enabled=enabled,
        prefix=prefix,
        domain=domain,
        title=env_vars.get("WEBSITE_TITLE", "Knowledge Base"),
        subtitle=env_vars.get("WEBSITE_SUBTITLE", "Project Documentation"),
        deploy_host=deploy_host,
        deploy_path=deploy_path,
        users=_parse_users(env_vars.get("WEBSITE_USERS", "")),
    )
