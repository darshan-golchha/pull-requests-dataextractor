import requests
import json
import csv
import pandas as pd
from tqdm import tqdm # type: ignore
import time
import ast
import os
import sys


# Global variables
repository = ''
vcs_url = ''
auth = ('', '')  # Username and password for Version Control System

def fetch_vcs_pull_requests():
    pull_requests = []
    url = vcs_url
    pbar = tqdm(desc="Fetching pull requests", unit="fetch")
    while url:
        response = requests.get(url, auth=auth)
        response.raise_for_status()
        data = response.json()
        pbar.update(len(data['values']))
        pull_requests.extend(data['values'])
        url = data.get('next')
    pbar.close()
    return pull_requests

# Store pull requests in a csv file
def store_pull_requests(pull_requests, filename="pull_requests.csv"):
    pbar = tqdm(desc="Storing pull requests", unit="store")
    with open(filename, 'a') as f:
        writer = csv.writer(f)
        for pr in pull_requests:
            pbar.update(1)
            id = pr['id']
            title = pr['title']
            description = pr['description']
            author = pr['author']['display_name'] if 'display_name' in pr['author'] else 'Unknown'
            date = pr['created_on']
            state = pr['state']
            source_branch = pr['source']['branch']['name']
            destination_branch = pr['destination']['branch']['name']
            closed_source_branch = pr['closed_source_branch'] if 'closed_source_branch' in pr else 'None'
            source_commit = pr['source']['commit']['hash']
            merge_commit = pr['merge_commit']['hash'] if pr['merge_commit'] and 'hash' in pr['merge_commit'] else 'None'
            destination_commit = pr['destination']['commit']['hash']
            closed_by = pr['closed_by']['display_name'] if pr["closed_by"] and 'display_name' in pr['closed_by'] else 'None'
            reason = pr['reason'] if 'reason' in pr else 'None'
            repository = pr['destination']['repository']['full_name']
            links = pr['links']
            writer.writerow([id, title, description, author, date, state, source_branch, destination_branch,
                             closed_source_branch, source_commit, merge_commit, destination_commit,
                             closed_by, reason, repository, links])
    pbar.close()

# Read pull requests from a csv file to a dataframe
def read_pull_requests(filename="pull_requests.csv"):
    df = pd.read_csv(filename)
    print(df.head())
    return df

def get_vcs_url(name="bitbucket",repository=""):
    global vcs_url
    if name == "bitbucket":
        vcs_url = 'https://api.bitbucket.org/2.0/repositories/' + repository + '/pullrequests?state=ALL'

def get_vcs_auth(auth_tuple):
    global auth
    if auth_tuple != ('', ''):
        auth = auth_tuple
    else:
        sys.exit("Invalid authentication details. Exiting...")

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

def get_pull_diffs():
    df = read_pull_requests()
    with open('diffs.csv', 'w') as f:
        # writing id, diff
        writer = csv.writer(f)
        writer.writerow(['ID', 'Diff'])
    pbar = tqdm(desc="Fetching diffs", unit="fetch")
    for index, row in df.iterrows():
        pbar.update(1)
        links = ast.literal_eval(row['Links'])
        diff_url = links['diff']['href']
        print(diff_url)
        response = requests.get(diff_url, auth=auth)
        response.raise_for_status()
        data = response.text
        with open('diffs.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow([row['ID'], data])
    pbar.close()

def combine_csv():
    df1 = pd.read_csv('pull_requests.csv')
    df2 = pd.read_csv('diffs.csv')
    df = pd.merge(df1, df2, on='ID')
    df.to_csv('combined.csv', index=False)

# writing the main function
if __name__ == "__main__":
    print("This script fetches pull requests and their diffs from")
    print("++++++++++++++++++++++++BITBUCKET+++++++++++++++++++++++++++++++")
    overwrite = input("Do you want to overwrite the existing csv files? (y/n): ")
    if overwrite == 'y':
        set_upcsv()
    print("Enter the username and password or leave blank for default")
    username = input("Enter username: ")
    password = input("Enter password: ")
    if username and password:
        get_vcs_auth((username, password))
    else:
        get_vcs_auth(('', ''))
    get_vcs_url("bitbucket", input("Enter the repository name: "))
    pull_requests = fetch_vcs_pull_requests()
    store_pull_requests(pull_requests)
    # get_pull_diffs()
    # combine_csv()
    print("Pull requests are stored in path: ", os.getcwd()+os.sep+"pull_requests.csv")