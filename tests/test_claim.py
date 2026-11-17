import pytest

from plextool import claim
from plextool.cli import build_parser
from plextool.common import PlexToolError


class Reply:
    def __init__(self, status=200, body=None):
        self.status_code, self._body = status, body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise claim.RequestException(f"status {self.status_code}")

    def json(self):
        if self._body is None:
            raise ValueError("no json")
        return self._body


def run_claim(monkeypatch, capsys, reply, *argv):
    seen = {}

    def fake_get(url, headers, timeout):
        seen.update(url=url, headers=headers)
        return reply

    monkeypatch.setattr(claim.requests, "get", fake_get)
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
    status, out, seen = run_claim(monkeypatch, capsys, Reply(body={"token": "claim-abc"}), *argv)
    assert status == 0
    assert out.out == expected + "\n"
    assert "4 minutes" in out.err
    assert seen["url"] == claim.CLAIM_URL
    assert seen["headers"]["X-Plex-Token"] == "secret"


def test_claim_reports_a_rejected_token(monkeypatch, capsys):
    with pytest.raises(PlexToolError, match="rejected the token"):
        run_claim(monkeypatch, capsys, Reply(status=401))


@pytest.mark.parametrize("body", [None, {}, {"token": "not-a-claim"}])
def test_claim_rejects_an_unexpected_reply(monkeypatch, capsys, body):
    with pytest.raises(PlexToolError):
        run_claim(monkeypatch, capsys, Reply(body=body))
