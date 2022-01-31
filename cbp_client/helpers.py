import os
from pathlib import Path
import json


def load_credentials(sandbox_mode):
    env_variable_prefix = 'sandbox_' if sandbox_mode else ''
    project_root = Path(__file__).parents[1].resolve()

    try:
        return json.loads((project_root / 'credentials.json').read_text())['sandbox']
    except FileNotFoundError:
        try:
            return {
                'api_key': os.environ[f'{env_variable_prefix}api_key'],
                'passphrase': os.environ[f'{env_variable_prefix}api_passphrase'],
                'secret': os.environ[f'{env_variable_prefix}api_secret']
            }
        except KeyError:
            raise Exception('Either pass your credentials explicitly '
                            'or set them as environment variables.\n'
                            f'\t{env_variable_prefix}api_key=[api_key]\n'
                            f'\t{env_variable_prefix}api_passphrase=[api_passphrase]\n'
                            f'\t{env_variable_prefix}api_secret=[api_secret]'
                            )
