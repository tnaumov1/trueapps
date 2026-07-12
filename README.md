# TrueAPPS

Deploy your custom TrueNAS apps via CLI

Based on the official TrueNAS [api client](https://github.com/truenas/api_client)

## Features

- Custom apps deployment via TrueNAS Scale API
- Skip app deploy if no changes are present against remote
- View a deployment summary of created, updated, skipped, and failed app deployment
- Dry run mode with pending deployment summary output

## Requirements

- Docker Compose (to complete and validate compose files)
- Python 3.14
- uv (available in PATH)
- TrueNAS Scale 25.10 and higher
- TrueNAS API key and username associated with it

## Installation

Install it as a standalone cli-tool from GitHub with `uv`

Latest version from `main`:

```bash
uv tool install git+https://github.com/tnaumov1/trueapps.git
```

Latest tagged release:

```bash
uv tool install git+https://github.com/tnaumov1/trueapps.git@v0.1.1
```

## Usage

### Using as installed cli-tool

If you did run `uv tool install` you can use it as a cli-app

```bash
trueapps --help
```

### Using `uv`

No `uv tool install` is required

```bash
uv run trueapps --help
```

## Upgrade

```bash
uv tool upgrade trueapps
```