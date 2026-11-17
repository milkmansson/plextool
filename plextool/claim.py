"""token claim: get a claim token from plex.tv, for starting a new Plex server in Docker."""

from __future__ import annotations

import argparse
import sys

import requests
from requests.exceptions import RequestException

from .common import SIGN_IN_AGAIN, PlexToolError, add_command, add_token_args, paint, resolve_token

CLAIM_URL = "https://plex.tv/api/claim/token.json"
CLAIM_VARIABLE = "PLEX_CLAIM"
VALID_MINUTES = 4

# How each --format shows the token. The token is the value on its own.
FORMATS = {
    "env": f"{CLAIM_VARIABLE}={{token}}",
    "compose": f"- {CLAIM_VARIABLE}={{token}}",
    "docker": f"-e {CLAIM_VARIABLE}={{token}}",
    "token": "{token}",
}


def fetch_claim_token(token: str) -> str:
    """Ask plex.tv for a claim token on behalf of the account that owns `token`."""
    try:
        response = requests.get(CLAIM_URL, headers={"X-Plex-Token": token, "Accept": "application/json",
                                                    "X-Plex-Product": "plextool"}, timeout=15)
    except RequestException as e:
        raise PlexToolError(f"Could not reach plex.tv: {e}") from None
    if response.status_code in (401, 403):
        raise PlexToolError(f"plex.tv rejected the token. {SIGN_IN_AGAIN}")
    try:
        response.raise_for_status()
        claim = response.json()["token"]
    except (RequestException, ValueError, KeyError) as e:
        raise PlexToolError(f"plex.tv did not return a claim token ({e}).") from None
    if not str(claim).startswith("claim-"):
        raise PlexToolError("plex.tv returned something that is not a claim token.")
    return claim


def run_claim(args: argparse.Namespace) -> int:
    token, _ = resolve_token(args)
    claim = fetch_claim_token(token)
    print(FORMATS[args.format].format(token=claim))
    print(paint(f"This claim token stops working after {VALID_MINUTES} minutes. Start the container before then. "
                "It only claims a server that is not claimed yet.", "yellow"), file=sys.stderr)
    return 0


def add_action(subparsers) -> None:
    """Add 'claim' as an action of 'plextool token'."""
    parser = add_command(
        subparsers, "claim", "get a claim token to set up a new server in Docker",
        "Prints a claim token from plex.tv, ready to paste into the Docker or Docker Compose setup for a new "
        "Plex Media Server, so the server is linked to the Plex account when it first starts. The token is "
        f"valid for {VALID_MINUTES} minutes and only claims a server that has not been claimed yet. The "
        "output is only the line asked for, so it can be used in a script; the reminder goes to standard error. "
        "Uses the saved login, or any token found the usual way.",
        ["plextool token claim",
         "plextool token claim --format compose",
         "plextool token claim --format docker",
         'PLEX_CLAIM=$(plextool token claim --format token) docker compose up -d'])
    add_token_args(parser)
    parser.add_argument("--format", choices=sorted(FORMATS), default="env",
                        help=f"env: {CLAIM_VARIABLE}=claim-... (for a .env file or the shell); compose: "
                             f"'- {CLAIM_VARIABLE}=claim-...' (a line under environment: in docker-compose.yml); "
                             f"docker: '-e {CLAIM_VARIABLE}=claim-...' (for docker run); token: the bare token "
                             "(default: env)")
