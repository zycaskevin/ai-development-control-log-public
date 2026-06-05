#!/usr/bin/env python3
"""Send a completed Daily AI Decision Digest to an opt-in channel.

Supported providers are deliberately simple and secret-driven:

- none: no external send
- slack: incoming webhook
- feishu: custom bot webhook
- telegram: bot token + chat id
- email_resend: Resend API

The script refuses to send an incomplete digest. It does not print secret
values in error messages.
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.request

import validate_daily_digest


SUPPORTED_PROVIDERS = ('none', 'slack', 'feishu', 'telegram', 'email_resend')
TELEGRAM_TOKEN_RE = re.compile(r'^[0-9]+:[A-Za-z0-9_-]+$')


class DeliveryConfigError(ValueError):
    """Configuration error whose message is safe to print."""


def _has_control_chars(value: str) -> bool:
    return any(ord(char) < 32 or ord(char) == 127 for char in value)


def _require_safe_value(name: str, value: str) -> str:
    if _has_control_chars(value):
        raise DeliveryConfigError(f'invalid {name}: contains unsupported control characters')
    return value


def _require_url_prefix(name: str, value: str, prefixes: tuple[str, ...]) -> str:
    value = _require_safe_value(name, value.strip())
    if not any(value.startswith(prefix) for prefix in prefixes):
        raise DeliveryConfigError(f'invalid {name}: unexpected webhook URL format')
    return value


def _require_telegram_token(value: str) -> str:
    value = _require_safe_value('TELEGRAM_BOT_TOKEN', value.strip())
    if not TELEGRAM_TOKEN_RE.fullmatch(value):
        raise DeliveryConfigError('invalid TELEGRAM_BOT_TOKEN: unexpected token format')
    return value


def _require_nonempty_list(name: str, values: list[str]) -> list[str]:
    if not values:
        raise DeliveryConfigError(f'invalid {name}: no recipient configured')
    return values


@dataclass(frozen=True)
class DeliveryRequest:
    url: str
    headers: dict[str, str]
    json_body: dict[str, object]


def required_env_names(provider: str) -> list[str]:
    if provider == 'none':
        return []
    if provider == 'slack':
        return ['SLACK_WEBHOOK_URL']
    if provider == 'feishu':
        return ['FEISHU_WEBHOOK_URL']
    if provider == 'telegram':
        return ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    if provider == 'email_resend':
        return ['RESEND_API_KEY', 'EMAIL_FROM', 'EMAIL_TO']
    raise ValueError(f'unsupported delivery provider: {provider}')


def validate_env(provider: str, env: dict[str, str]) -> list[str]:
    """Return missing env var names only; never return secret values."""
    return [name for name in required_env_names(provider) if not env.get(name)]


def _trim_digest_for_chat(text: str, limit: int = 3800) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit - 80].rstrip() + '\n\n…內容太長，請到 workflow artifact 看完整 digest。'


def build_delivery_request(
    provider: str,
    digest_text: str,
    env: dict[str, str],
) -> DeliveryRequest | None:
    """Build the HTTP request for a provider. Does not perform network IO."""
    provider = provider.strip().lower()
    if provider == 'none':
        return None

    missing = validate_env(provider, env)
    if missing:
        raise ValueError('missing required environment variables: ' + ', '.join(missing))

    body = _trim_digest_for_chat(digest_text)
    if provider == 'slack':
        return DeliveryRequest(
            url=_require_url_prefix(
                'SLACK_WEBHOOK_URL',
                env['SLACK_WEBHOOK_URL'],
                ('https://hooks.slack.com/services/',),
            ),
            headers={'Content-Type': 'application/json'},
            json_body={'text': body},
        )
    if provider == 'feishu':
        return DeliveryRequest(
            url=_require_url_prefix(
                'FEISHU_WEBHOOK_URL',
                env['FEISHU_WEBHOOK_URL'],
                (
                    'https://open.feishu.cn/open-apis/bot/v2/hook/',
                    'https://open.larksuite.com/open-apis/bot/v2/hook/',
                ),
            ),
            headers={'Content-Type': 'application/json'},
            json_body={'msg_type': 'text', 'content': {'text': body}},
        )
    if provider == 'telegram':
        token = _require_telegram_token(env['TELEGRAM_BOT_TOKEN'])
        chat_id = _require_safe_value('TELEGRAM_CHAT_ID', env['TELEGRAM_CHAT_ID'].strip())
        return DeliveryRequest(
            url=f'https://api.telegram.org/bot{token}/sendMessage',
            headers={'Content-Type': 'application/json'},
            json_body={
                'chat_id': chat_id,
                'text': body,
                'disable_web_page_preview': True,
            },
        )
    if provider == 'email_resend':
        api_key = _require_safe_value('RESEND_API_KEY', env['RESEND_API_KEY'].strip())
        email_from = _require_safe_value('EMAIL_FROM', env['EMAIL_FROM'].strip())
        email_to = _require_nonempty_list(
            'EMAIL_TO',
            [_require_safe_value('EMAIL_TO', addr.strip()) for addr in env['EMAIL_TO'].split(',') if addr.strip()],
        )
        return DeliveryRequest(
            url='https://api.resend.com/emails',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
            },
            json_body={
                'from': email_from,
                'to': email_to,
                'subject': 'Daily AI Decision Digest',
                'text': digest_text.strip(),
            },
        )

    raise ValueError(f'unsupported delivery provider: {provider}')


def send_request(request: DeliveryRequest) -> None:
    payload = json.dumps(request.json_body, ensure_ascii=False).encode('utf-8')
    req = urllib.request.Request(
        request.url,
        data=payload,
        headers=request.headers,
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=20) as response:  # noqa: S310 - user-provided webhook is intentional
        status = getattr(response, 'status', 200)
        if status >= 400:
            raise RuntimeError(f'delivery failed with HTTP {status}')


def main() -> int:
    parser = argparse.ArgumentParser(description='Send a completed daily digest to an opt-in channel.')
    parser.add_argument('digest_path', help='Path to daily digest markdown file.')
    parser.add_argument(
        '--provider',
        default=os.environ.get('DELIVERY_PROVIDER', 'none'),
        help='none | slack | feishu | telegram | email_resend. Defaults to DELIVERY_PROVIDER env or none.',
    )
    args = parser.parse_args()

    provider = args.provider.strip().lower()
    if provider not in SUPPORTED_PROVIDERS:
        print(f'ERROR: unsupported delivery provider: {provider}', file=sys.stderr)
        return 2

    if provider == 'none':
        print('Delivery provider is none; skipping external send.')
        return 0

    digest_path = Path(args.digest_path)
    errors = validate_daily_digest.validate_digest(digest_path)
    if errors:
        print('ERROR: digest is incomplete; refusing external send.', file=sys.stderr)
        for error in errors:
            print(f'- {error}', file=sys.stderr)
        return 3

    digest_text = digest_path.read_text(encoding='utf-8')
    try:
        request = build_delivery_request(provider, digest_text, dict(os.environ))
        if request is None:
            print('Delivery provider is none; skipping external send.')
            return 0
        send_request(request)
    except DeliveryConfigError as exc:
        print(f'ERROR: delivery configuration invalid for provider {provider}: {exc}', file=sys.stderr)
        return 4
    except ValueError as exc:
        # Missing variable names are safe; unsupported providers are rejected earlier.
        print(f'ERROR: delivery configuration invalid for provider {provider}: {exc}', file=sys.stderr)
        return 4
    except urllib.error.HTTPError as exc:
        print(f'ERROR: delivery failed for provider {provider}: HTTP {exc.code}', file=sys.stderr)
        return 4
    except Exception:
        # Never print raw network/URL/header exceptions: they can include
        # webhook URLs, bot tokens, API keys, or Authorization headers.
        print(
            f'ERROR: delivery failed for provider {provider}: invalid delivery configuration or network error',
            file=sys.stderr,
        )
        return 4

    print(f'Delivery sent via {provider}.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
