import requests
import json
import csv
import pandas as pd
from tqdm import tqdm # type: ignore
import time
import ast
import os


# Global variables
repository = ''
vcs_url = ''  # URL for Version Control System
auth = ('', '')  # Username and password for Version Control System


def fetch_vcs_pull_requests():
    pull_requests = []
    url = vcs_url
    pbar = tqdm(desc="Fetching pull requests", unit="fetch")
    while url:
        try:
            if len(pull_requests) > 400:
                break
            response = requests.get(url, auth=auth)
            response.raise_for_status()
            data = response.json()
            pbar.update(len(data))
            pull_requests.extend(data)
            url = response.links.get('next', {}).get('url')
        except Exception as e:
            pbar.close()
            return pull_requests
    pbar.close()
    return pull_requests


def get_vcs_url(name="github", repository=""):
    global vcs_url
    if name == "github":
        vcs_url = f'https://api.github.com/repos/{repository}/pulls?state=all'


def get_vcs_auth(token):
    global auth
    if type(token) == str:
        auth = ('token', token)
    else:
        print("Please note that using username and password is not recommended.")
        auth = token

# Store pull requests in a csv file
def store_pull_requests(pull_requests, filename="pull_requests.csv"):
    pbar = tqdm(desc="Storing pull requests", unit="store")
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for pr in pull_requests:
            pbar.update(1)
            id = pr['id']
            title = pr['title']
            description = pr['body']
            author = pr['user']['login']
            date = pr['created_at']
            state = pr['state']
            source_branch = pr['head']['ref']
            destination_branch = pr['base']['ref']
            closed_source_branch = pr['head']['repo']['default_branch'] if pr['head']['repo']['default_branch'] else 'None'
            source_commit = pr['head']['sha']
            merge_commit = pr['merge_commit_sha'] if pr['merge_commit_sha'] else 'None'
            destination_commit = pr['base']['sha']
            closed_by = pr['head']['user']['login'] if pr['head'] and pr['head']['user'] else 'None'
            reason = pr['state']
            repository = pr['base']['repo']['full_name']
            links = {'self': pr['html_url'], 'diff': pr['diff_url']}
            writer.writerow([id, title, description, author, date, state, source_branch, destination_branch,
                             closed_source_branch, source_commit, merge_commit, destination_commit,
                             closed_by, reason, repository, json.dumps(links)])
    pbar.close()

def set_upcsv():
    with open('pull_requests.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Description', 'Author', 'Date', 'State',
                            'Source Branch', 'Destination Branch','Closed Source Branch',
                            'Source Commit','Merge Commit', 'Destination Commit','Closed By',
                            'Reason','Repository', 'Links'
                         ])
        
    with open('diffs.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Diff'])

if __name__ == "__main__":
    print("This script fetches pull requests and their diffs from GitHub.")
    overwrite = input("Do you want to overwrite the existing csv files? (y/n): ")
    if overwrite == 'y':
        set_upcsv()
    print("Enter your GitHub token or leave blank for username/password.")
    token = input("Enter token: ")
    if token:
        get_vcs_auth(token)
    else:
        get_vcs_auth('')
    get_vcs_url("github", input("Enter the repository name: "))
    pull_requests = fetch_vcs_pull_requests()
    store_pull_requests(pull_requests)

    # UNCOMMENT THE FOLLOWING FUNCTIONS TO GET THE DIFFS
    # get_pull_diffs()
    # combine_csv()
    
    print("Pull requests are stored in path: ", os.getcwd() + os.sep + "pull_requests.csv")