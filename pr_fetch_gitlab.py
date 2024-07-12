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
            # Getting the next page URL
            url = response.links.get('next', {}).get('url')
        except Exception as e:
            pbar.close()
            return pull_requests
    pbar.close()
    return pull_requests



def get_vcs_url(name="gitlab", repository=""):
    global vcs_url
    if name == "gitlab":
        vcs_url = f'https://gitlab.com/api/v4/projects/{repository}/merge_requests?state=all'



def get_vcs_auth(token):
    global auth
    if type(token) == str:
        auth = ('private_token', token)
    else:
        auth = token


def store_pull_requests(pull_requests, filename="pull_requests.csv"):
    pbar = tqdm(desc="Storing pull requests", unit="store")
    with open(filename, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        for pr in pull_requests:
            pbar.update(1)
            id = pr['id']
            title = pr['title']
            description = pr['description']
            author = pr['author']['username'] if 'username' in pr['author'] else 'Unknown'
            date = pr['created_at']
            state = pr['state']
            source_branch = pr['source_branch']
            destination_branch = pr['target_branch']
            closed_source_branch = pr['source_branch']
            source_commit = pr['sha']
            merge_commit = pr['merge_commit_sha'] if 'merge_commit_sha' in pr else 'None'
            destination_commit = pr['merge_commit_sha'] if 'merge_commit_sha' in pr else 'None'
            closed_by = pr['merged_by']['username'] if pr['merged_by'] and 'username' in pr['merged_by'] else 'None'
            writer.writerow([id, title, description, author, date, state, source_branch, destination_branch,
                             closed_source_branch, source_commit, merge_commit, destination_commit,
                             closed_by])
    pbar.close()

def set_upcsv():
    with open('pull_requests.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Title', 'Description', 'Author', 'Date', 'State',
                            'Source Branch', 'Destination Branch','Closed Source Branch',
                            'Source Commit','Merge Commit', 'Destination Commit','Closed By'
                         ])
        
    with open('diffs.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'Diff'])

if __name__ == "__main__":
    print("This script fetches pull requests and their details from GitLab.")
    overwrite = input("Do you want to overwrite the existing csv files? (y/n): ")
    if overwrite.lower() == 'y':
        set_upcsv()
    
    print("Enter your GitLab private token or leave blank for username/password.")
    token = input("Enter token: ")
    if token:
        get_vcs_auth(token)
    else:
        get_vcs_auth('')
    
    srch_option = int(input("Enter 1 to search by project ID or 2 to search by (username,project): "))
    if srch_option == 1:
        repository_name = input("Enter the project ID: ")
    elif srch_option == 2:
        username = input("Enter the username: ")
        project = input("Enter the project name: ")
        repository_name = f"{username}%2F{project}"
    else:
        print("Invalid input. Exiting...")
        exit()
    
    get_vcs_url("gitlab", repository_name)
    
    pull_requests = fetch_vcs_pull_requests()
    store_pull_requests(pull_requests)
    
    print("Pull requests are stored in path:", os.getcwd() + os.sep + "pull_requests.csv")
