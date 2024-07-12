import os
import sys
import getpass
import importlib
from tqdm import tqdm
from requests.auth import HTTPBasicAuth


# Global Default Auths
auths = {
    "gitlab": "<DEFAULT GITLAB TOKEN>",
    "github": "<DEFAULT GITHUB TOKEN>",
    "bitbucket": ('<DEFAULT BITBUCKET USERNAME>','<DEFAULT BITBUCKET APP PASSWORD>')
}

# Importing methods from respective VCS files
vcs_modules = {
    "gitlab": "pr_fetch_gitlab",
    "github": "pr_fetch_github",
    "bitbucket": "pr_fetch_bitbucket"
}

def load_vcs_module(vcs_name):
    if vcs_name in vcs_modules:
        return importlib.import_module(vcs_modules[vcs_name])
    else:
        print("Invalid VCS type. Exiting...")
        sys.exit()

def main():
    print("Welcome to the VCS Pull Requests Fetcher")
    print("========================================")
    print("Select your Version Control System (VCS):")
    print("1. GitLab")
    print("2. GitHub")
    print("3. Bitbucket")

    vcs_choice = input("Enter the number corresponding to your VCS: ")

    if vcs_choice == '1':
        vcs_name = 'gitlab'
    elif vcs_choice == '2':
        vcs_name = 'github'
    elif vcs_choice == '3':
        vcs_name = 'bitbucket'
    else:
        print("Invalid choice. Exiting...")
        sys.exit()

    vcs_module = load_vcs_module(vcs_name)
    
    print(f"Selected VCS: {vcs_name.capitalize()}")
    overwrite = input("Do you want to overwrite the existing csv files? (y/n): ")
    if overwrite.lower() == 'y':
        vcs_module.set_upcsv()

    print("Do you want to authenticate Manually or use Default credentials?")
    print("1. Manually")
    print("2. Default")
    auth_choice = input("Enter the number corresponding to your choice: ")
    if auth_choice == '1':
        print("Enter your authentication details:")
        if vcs_name in ["gitlab", "github"]:
            token = getpass.getpass("Enter your personal access token (or leave blank for username/password): ")
            if token:
                vcs_module.get_vcs_auth(token)
            else:
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")
                vcs_module.get_vcs_auth(HTTPBasicAuth(username, password))
        elif vcs_name == "bitbucket":
            username = input("Enter username: ")
            password = getpass.getpass("Enter access token: ")
            vcs_module.get_vcs_auth((username, password))
    elif auth_choice == '2':
        vcs_module.get_vcs_auth(auths[vcs_name])

    if vcs_name in ["gitlab", "github"]:
        srch_option = int(input("Enter 1 to search by project ID or 2 project URL: "))
        if srch_option == 1:
            repository_name = input("Enter the project ID: ")
        elif srch_option == 2:
            url = input("Enter the Git URL: ")
            username = url.split("/")[-2]
            project = url.split("/")[-1].split(".")[0]
            repository_name = f"{username}%2F{project}"
        else:
            print("Invalid input. Exiting...")
            sys.exit()
    else:
        repository_url = input("Enter the repository url:")
        repository_name = repository_url.split("/")[-2]+ "%2F" + repository_url.split("/")[-1].split(".")[0]

    vcs_module.get_vcs_url(vcs_name, repository_name)

    print(f"Fetching pull requests from {vcs_name.capitalize()}...")
    pull_requests = vcs_module.fetch_vcs_pull_requests()
    vcs_module.store_pull_requests(pull_requests)

    print(f"Pull requests are stored in path: {os.getcwd() + os.sep + 'pull_requests.csv'}")

if __name__ == "__main__":
    main()
