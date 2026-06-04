import argparse
import logging
import os
import subprocess
import sys
from argparse import ArgumentParser
from pathlib import Path
from subprocess import CompletedProcess

from truenas_api_client import Client

from trueapps import try_deploy_app, login_with_api_key, discover_apps, find_app_compose, setup_logging

log = logging.getLogger(__name__)


def run() -> int:
    parser = define_args_parser()
    args = parser.parse_args()

    if args.api_key is None:
        args.api_key = os.environ.get("TRUENAS_API_KEY")
    if not args.api_key:
        parser.error("--api-key is required (or set the TRUENAS_API_KEY environment variable)")

    created = updated = skipped = failed = 0

    apps_paths: list[Path] = discover_apps(args.apps_dir, args.apps)

    apps = {}
    for app_path in apps_paths:
        response = find_app_compose(app_path)
        if response is not None:
            app_name, app_compose_path = response
            apps[app_name] = app_compose_path

    apps_yaml = {}
    for app_name, app_compose_path in apps.items():
        config: CompletedProcess[str] = subprocess.run(
            args=["docker", "compose", "-f", str(app_compose_path), "config", "--format", "yaml"],
            text=True, capture_output=True, timeout=30)
        if config.returncode != 0:
            log.warning("Skipping app %s cause of failed compose validation! Error: %s",
                        app_name, config.stderr)
            failed += 1
        else:
            apps_yaml[app_name] = config.stdout

    if len(apps_yaml) == 0:
        log.info("No apps to deploy. Exiting...")
        return 2

    if args.print_apps:
        for app_name, app_compose_yaml in apps_yaml.items():
            log.info("\n--- %s ---\n%s", app_name, app_compose_yaml)

    with Client(f"wss://{args.host}:{args.port}/api/current", verify_ssl=(not args.ignore_ssl)) as client:
        response = login_with_api_key(client, args.username, args.api_key)

        if response.get("response_type") != "SUCCESS":
            raise RuntimeError(f"auth failed: {response}")

        for app_name, app_compose_yaml in apps_yaml.items():
            try:
                result = try_deploy_app(client, app_name, app_compose_yaml, dry_run=args.dry_run)
            except Exception as ex:
                failed += 1
                log.error("failed [%s]: %s", app_name, ex)
                continue
            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
            else:
                skipped += 1

    log.info("summary: %d created, %d updated, %d skipped, %d failed",
             created, updated, skipped, failed)
    if failed > 0:
        return 1
    return 0


def define_args_parser() -> ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", help="TrueNAS Scale API host (e.g. truenas.local)", required=True)
    parser.add_argument("--port", help="TrueNAS Scale API port (e.g. 443)", default=443, type=int)
    parser.add_argument("--api-key", help="TrueNAS Scale API key (or set TRUENAS_API_KEY env var)")
    parser.add_argument("--username", help="TrueNAS Scale API key username", required=True)
    parser.add_argument("--apps", help="deploy only this app")
    parser.add_argument(
        "--ignore-ssl",
        action="store_true",
        help="ignore issues with SSL certificates when accessing TrueNAS API",
    )
    parser.add_argument(
        "--apps-dir",
        type=Path,
        default='apps/',
        help="custom apps root dir, defaults to apps/"
    )
    parser.add_argument(
        "--print-apps",
        action="store_true",
        help="print resolved compose for each app; does not call TrueNAS API",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="run a dry run and print summary; does not deploy"
    )
    return parser

def main() -> None:
    setup_logging()
    try:
        sys.exit(run())
    except Exception as exc:
        log.exception(exc)
        sys.exit(-1)

if __name__ == "__main__":
    main()