"""Check and fix collection visibility"""
import requests
from config import DIRECTUS_URL, DIRECTUS_EMAIL, DIRECTUS_PASSWORD

resp = requests.post(f'{DIRECTUS_URL}/auth/login', json={'email': DIRECTUS_EMAIL, 'password': DIRECTUS_PASSWORD})
token = resp.json()['data']['access_token']
headers = {'Authorization': f'Bearer {token}'}

collections = ['instruction_type', 'callsign_format', 'radiocall', 'radiocall_instruction', 
               'acceptable_variation', 'common_error', 'radiocall_set', 'radiocall_set_items']

print("Checking collection metadata...\n")

for coll in collections:
    resp = requests.get(f'{DIRECTUS_URL}/collections/{coll}', headers=headers)
    if resp.status_code == 200:
        data = resp.json()['data']
        meta = data.get('meta') or {}
        print(f'{coll}:')
        print(f'  hidden: {meta.get("hidden")}')
        print(f'  singleton: {meta.get("singleton")}')
        print(f'  icon: {meta.get("icon")}')
        print(f'  group: {meta.get("group")}')
        
        # Fix if hidden
        if meta.get('hidden'):
            print(f'  --> Unhiding...')
            fix = requests.patch(
                f'{DIRECTUS_URL}/collections/{coll}',
                headers=headers,
                json={'meta': {'hidden': False}}
            )
            print(f'  --> Status: {fix.status_code}')
    else:
        print(f'{coll}: NOT FOUND ({resp.status_code})')
    print()
