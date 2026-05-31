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

## Usage

### Using `uv`

View all arguments and description

```bash
uv run trueapps.py --help
```
