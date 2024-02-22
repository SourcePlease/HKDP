import contextlib
from logging import FileHandler, StreamHandler, INFO, basicConfig, error as log_error, info as log_info
from os import path as ospath, environ
from subprocess import run as srun, call as scall
from dotenv import load_dotenv
import pkg_resources, requests, os

if ospath.exists('log.txt'):
    with open('log.txt', 'r+') as f:
        f.truncate(0)

basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[FileHandler('log.txt'), StreamHandler()],
                    level=INFO)

def get_config_from_url(configurl: str):
    try:
        if os.path.isfile('config.env'):
            with contextlib.suppress(Exception):
                os.remove('config.env')
        if ' ' in configurl:
            log_info("Detected gitlab snippet url. Example: 26265 sdg6-626-g6256")
            snipid, apikey = configurl.split(maxsplit=1)
            main_api = f"https://gitlab.com/api/v4/snippets/{snipid}/raw"
            headers = {'content-type': 'application/json', 'PRIVATE-TOKEN': apikey}
            res = requests.get(main_api, headers=headers)
        else:
            res = requests.get(configurl)
        if res.status_code == 200:
            log_info("Config retrieved remotely. Status 200.")
            with open('config.env', 'wb+') as f:
                f.write(res.content)
            load_dotenv('config.env', override=True)
        else:
            log_error(f"Failed to download config.env {res.status_code}")
    except Exception as e:
        log_error(f"CONFIG_FILE_URL: {e}")

if CONFIG_FILE_URL := os.environ.get('CONFIG_FILE_URL', None):
    if CONFIG_FILE_URL: get_config_from_url(CONFIG_FILE_URL)
else:
    log_error("Using local config.env")

# update packages +
if environ.get('UPDATE_EVERYTHING_WHEN_RESTART', 'False').lower() == 'true':
    packages = [dist.project_name for dist in pkg_resources.working_set]
    scall("pip install --upgrade " + ' '.join(packages), shell=True)
# update packages -

REPO_URL = environ.get('REPO_URL')

if ospath.exists('.git'):
    srun(["rm", "-rf", ".git"])
if ospath.isdir('SPUP'):
    srun(["rm", "-rf", "SPUP"])

update = srun([f"git init -q \
                 && git config --global user.email huzunluartemis@tuta.io \
                 && git config --global user.name huzunluartemis \
                 && git clone {REPO_URL}"], shell=True)

if update.returncode == 0:
    log_info('Retrieved files from the specified repository.')
else:
    log_error('Something went wrong. Check REPO_URL.')
    exit(1)
