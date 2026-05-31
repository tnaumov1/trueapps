import logging

from truenas_api_client import Client

from utils.apps import compose_equal

log = logging.getLogger(__name__)


def try_deploy_app(client: Client, app_name: str, app_compose_yaml: str, dry_run: bool = False) -> str:
    existing = client.call("app.query", [["name", "=", app_name]])
    if existing:
        current_config = client.call("app.config", app_name) or {}
        if compose_equal(app_compose_yaml, current_config):
            log.info("unchanged [%s]", app_name)
            return "skipped"
        if dry_run:
            log.info("update [%s]", app_name)
            return "updated"
        result = client.call(
            "app.update",
            app_name,
            {"custom_compose_config_string": app_compose_yaml},
            job=True,
        )
        action = "updated"
    else:
        if dry_run:
            log.info("create [%s]", app_name)
            return "created"
        result = client.call(
            "app.create",
            {
                "app_name": app_name,
                "custom_app": True,
                "custom_compose_config_string": app_compose_yaml,
            },
            job=True,
        )
        action = "created"
    state = result.get("state", "?")
    log.info("%s [%s] state=%s", action, app_name, state)
    return action

def login_with_api_key(client: Client, username: str, api_key: str) -> dict:
    response = client.call(
        "auth.login_ex",
        {"mechanism": "API_KEY_PLAIN", "username": username, "api_key": api_key},
    )
    return response