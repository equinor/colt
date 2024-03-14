import os
from github import *
from datetime import date
from LibraryBuilder import *

if __name__ == "__main__":
    access_token = os.environ.get("GITHUB_TOKEN")
    repo_url = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")

    if repo_url is None or access_token is None:
        raise ValueError("Failed to find token or repository URL.")
    
    from_dir = os.environ.get("INPUT_FROM")
    to_dir = os.environ.get("INPUT_TO")

    print(f"From: {from_dir}")
    print(f"To: {to_dir}")

    token = Auth.Token(access_token)
    
    github = Github(auth=token)

    ready_library(f"{repo_url}:{sha}")
    all_ontologies()

    repo = github.get_repo(repo_url)
    branch_name = f"colt/{date.today()}"

    default_branch = repo.get_branch(repo.default_branch)

    new_branch = repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=default_branch.commit.sha)

    author = InputGitAuthor(
        "GitHub Action",
        "action@github.com"
    )

    new_files_dir = os.path.join(os.getcwd(), "nuget")

    new_files = [file for file in os.listdir(new_files_dir)]

    commit_message = "Added code libraries for ontologies."
    for file in new_files:
        with open(file, "r") as f:
            data = f.read()
        blob = repo.create_git_blob(data, "utf-8")
        tree = repo.create_git_tree([{
            "path": file,
            "mode": "100644",
            "type": "blob",
            "sha": blob.sha
        }], base_tree=default_branch.commit.sha)

        commit = repo.create_git_commit(commit_message, tree, [default_branch.commit.sha])
        new_branch.update(commit.sha)

    try:
        pr_title = f"COLT ./- Generated code library - {date.today()}"
        pr_body = "Plz check files."
        pr = repo.create_pull(title=pr_title, body=pr_body, head=new_branch, base=default_branch.name)
    except GithubException as ex:
        print(f"Failed to create pull request: {ex}")

    