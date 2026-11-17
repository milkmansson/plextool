import pytest
from plexapi.exceptions import Unauthorized

from plextool import claim
from plextool.cli import build_parser
from plextool.common import PlexToolError


def run_claim(monkeypatch, capsys, result, *argv):
    seen = {}

    class Account:
        def __init__(self, token):
            seen["token"] = token

        def claimToken(self):
            if isinstance(result, Exception):
                raise result
            return result

    monkeypatch.setattr(claim, "MyPlexAccount", Account)
    monkeypatch.setattr(claim, "resolve_token", lambda args: ("secret", "test"))
    args = build_parser().parse_args(["token", "claim", *argv])
    status = args.run(args)
    return status, capsys.readouterr(), seen


@pytest.mark.parametrize("fmt, expected", [
    (None, "PLEX_CLAIM=claim-abc"),
    ("env", "PLEX_CLAIM=claim-abc"),
    ("compose", "- PLEX_CLAIM=claim-abc"),
    ("docker", "-e PLEX_CLAIM=claim-abc"),
    ("token", "claim-abc"),
])
def test_claim_prints_only_the_requested_line(monkeypatch, capsys, fmt, expected):
    argv = ["--format", fmt] if fmt else []
    status, out, seen = run_claim(monkeypatch, capsys, "claim-abc", *argv)
    assert status == 0
    assert out.out == expected + "\n"
    assert "4 minutes" in out.err
    assert seen["token"] == "secret"


def test_claim_reports_a_rejected_token(monkeypatch, capsys):
    with pytest.raises(PlexToolError, match="rejected the token"):
        run_claim(monkeypatch, capsys, Unauthorized("401"))


@pytest.mark.parametrize("result", ["", "not-a-claim"])
def test_claim_rejects_an_unexpected_reply(monkeypatch, capsys, result):
    with pytest.raises(PlexToolError):
        run_claim(monkeypatch, capsys, result)
