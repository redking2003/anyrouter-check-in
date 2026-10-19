import json

from utils.config import AppConfig, ProviderConfig, load_accounts_config


def test_builtin_provider_profile_persistence_defaults(monkeypatch):
	monkeypatch.delenv('PROVIDERS', raising=False)

	config = AppConfig.load_from_env()

	assert list(config.providers.keys()) == ['anyrouter']
	assert config.providers['anyrouter'].persist_profile is True


def test_provider_profile_persistence_can_override_anyrouter(monkeypatch):
	monkeypatch.setenv(
		'PROVIDERS',
		json.dumps({'anyrouter': {'domain': 'https://anyrouter.top', 'persist_profile': False}}),
	)

	config = AppConfig.load_from_env()

	assert list(config.providers.keys()) == ['anyrouter']
	assert config.providers['anyrouter'].persist_profile is False


def test_non_anyrouter_providers_are_ignored(monkeypatch):
	monkeypatch.setenv(
		'PROVIDERS',
		json.dumps(
			{
				'agentrouter': {'domain': 'https://agentrouter.org', 'persist_profile': True},
				'custom': {'domain': 'https://custom.example.com'},
			}
		),
	)

	config = AppConfig.load_from_env()

	assert list(config.providers.keys()) == ['anyrouter']


def test_provider_from_dict_inherits_profile_persistence_from_defaults():
	defaults = ProviderConfig(name='anyrouter', domain='https://old.example.com', persist_profile=True)

	provider = ProviderConfig.from_dict(
		'anyrouter',
		{'domain': 'https://new.example.com'},
		defaults=defaults,
	)

	assert provider.persist_profile is True


def test_load_accounts_accepts_default_and_anyrouter_provider(monkeypatch):
	monkeypatch.setenv(
		'ANYROUTER_ACCOUNTS',
		json.dumps(
			[
				{'cookies': {'session': 's1'}, 'api_user': 'u1'},
				{'provider': ' AnyRouter ', 'cookies': {'session': 's2'}, 'api_user': 'u2'},
			]
		),
	)

	accounts = load_accounts_config()

	assert accounts is not None
	assert len(accounts) == 2
	assert [account.provider for account in accounts] == ['anyrouter', 'anyrouter']


def test_load_accounts_skips_non_anyrouter_provider(monkeypatch):
	monkeypatch.setenv(
		'ANYROUTER_ACCOUNTS',
		json.dumps(
			[
				{'provider': 'agentrouter', 'cookies': {'session': 's1'}, 'api_user': 'u1'},
				{'provider': 'custom', 'cookies': {'session': 's2'}, 'api_user': 'u2'},
				{'provider': 'anyrouter', 'cookies': {'session': 's3'}, 'api_user': 'u3'},
			]
		),
	)

	accounts = load_accounts_config()

	assert accounts is not None
	assert len(accounts) == 1
	assert accounts[0].provider == 'anyrouter'
