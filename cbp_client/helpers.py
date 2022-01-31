import os
from pathlib import Path
import json


def load_credentials(sandbox_mode):
    env_variable_prefix = 'sandbox_' if sandbox_mode else ''
    current_working_directory = Path().cwd()
    creds_file_path = current_working_directory / 'credentials.json'
    creds_json_key = 'sandbox' if sandbox_mode else 'live'

    try:
        return json.loads(creds_file_path.read_text())[creds_json_key]
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
