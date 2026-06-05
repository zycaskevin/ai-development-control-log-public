"""Tests for send_daily_digest.py — optional digest delivery."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))

import send_daily_digest  # noqa: E402


def test_required_env_names_for_supported_providers():
    assert send_daily_digest.required_env_names('none') == []
    assert send_daily_digest.required_env_names('slack') == ['SLACK_WEBHOOK_URL']
    assert send_daily_digest.required_env_names('feishu') == ['FEISHU_WEBHOOK_URL']
    assert send_daily_digest.required_env_names('telegram') == [
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHAT_ID',
    ]
    assert send_daily_digest.required_env_names('email_resend') == [
        'RESEND_API_KEY',
        'EMAIL_FROM',
        'EMAIL_TO',
    ]


def test_validate_env_reports_missing_names_without_secret_values():
    env = {'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/SECRET'}

    missing = send_daily_digest.validate_env('telegram', env)

    assert missing == ['TELEGRAM_BOT_TOKEN', 'TELEGRAM_CHAT_ID']
    assert 'SECRET' not in repr(missing)


def test_build_request_none_provider_skips_delivery():
    request = send_daily_digest.build_delivery_request(
        provider='none',
        digest_text='hello',
        env={},
    )

    assert request is None


def test_build_slack_request():
    request = send_daily_digest.build_delivery_request(
        provider='slack',
        digest_text='digest body',
        env={'SLACK_WEBHOOK_URL': 'https://hooks.slack.com/services/T/SECRET'},
    )

    assert request is not None
    assert request.url == 'https://hooks.slack.com/services/T/SECRET'
    assert request.headers['Content-Type'] == 'application/json'
    assert request.json_body == {'text': 'digest body'}


def test_build_feishu_request():
    request = send_daily_digest.build_delivery_request(
        provider='feishu',
        digest_text='digest body',
        env={'FEISHU_WEBHOOK_URL': 'https://open.feishu.cn/open-apis/bot/v2/hook/SECRET'},
    )

    assert request is not None
    assert request.url.endswith('/SECRET')
    assert request.json_body == {
        'msg_type': 'text',
        'content': {'text': 'digest body'},
    }


def test_build_telegram_request():
    request = send_daily_digest.build_delivery_request(
        provider='telegram',
        digest_text='digest body',
        env={
            'TELEGRAM_BOT_TOKEN': '123:SECRET',
            'TELEGRAM_CHAT_ID': '-100123',
        },
    )

    assert request is not None
    assert request.url == 'https://api.telegram.org/bot123:SECRET/sendMessage'
    assert request.json_body['chat_id'] == '-100123'
    assert request.json_body['text'] == 'digest body'


def test_build_resend_email_request():
    request = send_daily_digest.build_delivery_request(
        provider='email_resend',
        digest_text='digest body',
        env={
            'RESEND_API_KEY': 're_SECRET',
            'EMAIL_FROM': 'digest@example.com',
            'EMAIL_TO': 'boss@example.com',
        },
    )

    assert request is not None
    assert request.url == 'https://api.resend.com/emails'
    assert request.headers['Authorization'] == 'Bearer re_SECRET'
    assert request.json_body['to'] == ['boss@example.com']
    assert request.json_body['subject'].startswith('Daily AI Decision Digest')


def test_unknown_provider_is_rejected():
    try:
        send_daily_digest.required_env_names('discord')
    except ValueError as exc:
        assert 'unsupported delivery provider' in str(exc)
    else:
        raise AssertionError('expected ValueError')


def test_delivery_config_error_does_not_include_secret_url():
    secret_url = 'SECRET_URL_SHOULD_NOT_APPEAR'

    try:
        send_daily_digest.build_delivery_request(
            provider='slack',
            digest_text='digest body',
            env={'SLACK_WEBHOOK_URL': secret_url},
        )
    except send_daily_digest.DeliveryConfigError as exc:
        assert secret_url not in str(exc)
        assert 'SLACK_WEBHOOK_URL' in str(exc)
    else:
        raise AssertionError('expected DeliveryConfigError')


def test_main_malformed_telegram_token_does_not_leak_secret(monkeypatch, capsys):
    secret = 'SECRET_TOKEN_SHOULD_NOT_APPEAR'
    digest_path = Path(__file__).resolve().parents[1] / 'examples' / 'daily-decision-digest.zh-TW.md'
    monkeypatch.setattr(
        sys,
        'argv',
        ['send_daily_digest.py', str(digest_path), '--provider', 'telegram'],
    )
    monkeypatch.setenv('TELEGRAM_BOT_TOKEN', f'123:{secret} BAD')
    monkeypatch.setenv('TELEGRAM_CHAT_ID', '-100123')

    exit_code = send_daily_digest.main()

    captured = capsys.readouterr()
    assert exit_code == 4
    assert secret not in captured.err
    assert 'TELEGRAM_BOT_TOKEN' in captured.err
    assert 'Traceback' not in captured.err


def test_main_network_exception_does_not_leak_webhook(monkeypatch, capsys):
    secret_url = 'https://' + 'hooks.slack.com' + '/services/T/SECRET_SHOULD_NOT_APPEAR'
    digest_path = Path(__file__).resolve().parents[1] / 'examples' / 'daily-decision-digest.zh-TW.md'

    def fake_send_request(_request):
        raise RuntimeError(f'network failed for {secret_url}')

    monkeypatch.setattr(send_daily_digest, 'send_request', fake_send_request)
    monkeypatch.setattr(
        sys,
        'argv',
        ['send_daily_digest.py', str(digest_path), '--provider', 'slack'],
    )
    monkeypatch.setenv('SLACK_WEBHOOK_URL', secret_url)

    exit_code = send_daily_digest.main()

    captured = capsys.readouterr()
    assert exit_code == 4
    assert 'SECRET_SHOULD_NOT_APPEAR' not in captured.err
    assert secret_url not in captured.err
    assert 'invalid delivery configuration or network error' in captured.err
