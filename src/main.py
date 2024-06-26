import os
from github import *
from datetime import datetime
from uuid import uuid4
from LibraryBuilder import *


if __name__ == "__main__":
    access_token = os.environ.get("GITHUB_TOKEN")
    repo_url = os.environ.get("GITHUB_REPOSITORY")
    sha = os.environ.get("GITHUB_SHA")

    if repo_url is None or access_token is None:
        raise ValueError("Failed to find token or repository URL.")

    dotnet_version = os.environ.get("INPUT_DOTNET")
    if dotnet_version != None and dotnet_version not in ["6", "7", "8"]:
        raise Exception(".NET version not supported.")

    from_dir = os.environ.get("INPUT_FROM")
    to_dir = os.environ.get("INPUT_TO")

    root = os.getcwd()
    to_path = os.path.abspath(os.path.join(root, to_dir))
    from_path = os.path.abspath(os.path.join(root, from_dir))
    if os.path.commonprefix([to_path, root]) != root or os.path.commonprefix([from_path, root]) != root:
        raise Exception("Invalid path in INPUT_TO or INPUT_FROM.")
    if not os.path.exists(to_path):
        print(f"Created folders {to_path}")
        os.makedirs(to_path)

    print(f"From: {from_dir}")
    print(f"To: {to_dir}")

    token = Auth.Token(access_token)

    github = Github(auth=token)

    ready_library(f"{repo_url}:{sha}")
    all_ontologies()

    now = datetime.now().strftime("%Y-%m-%d_%H-%M")
    repo = github.get_repo(repo_url)
    unique_suffix = str(uuid4())[:5]
    branch_name = f"colt/{now}/{unique_suffix}"  # Short UUID because we want a unique aspect to avoid collisions in time, but it does not need to be globally unique

    default_branch = repo.get_branch(repo.default_branch)

    author = InputGitAuthor("GitHub Action", "action@github.com")

    new_files = [file for file in os.listdir(to_path)]

    changes = []
    for file in new_files:
        file_path = os.path.join(to_path, file)
        file_path = file_path.replace("/github/workspace/", "")
        print(f"Reading {file_path}")

        with open(file_path, "r") as f:
            data = f.read()
        blob = repo.create_git_blob(data, "utf-8")

        element = InputGitTreeElement(
            path=file_path, mode="100644", type="blob", sha=blob.sha
        )
        print(f"Added {file} to changes.")
        changes.append(element)

    head_sha = default_branch.commit.sha
    new_branch = repo.create_git_ref(
        ref=f"refs/heads/{branch_name}", sha=default_branch.commit.sha
    )
    print(f"Created branch {new_branch}")
    new_branch_sha = repo.get_branch(branch_name).commit.sha

    base_tree = repo.get_git_tree(sha=new_branch_sha)
    tree = repo.create_git_tree(changes, base_tree)

    parent = repo.get_git_commit(sha=new_branch_sha)

    commit_message = "Added code libraries for ontologies."
    commit = repo.create_git_commit(commit_message, tree, [parent])

    print(f"Created commit {commit.sha}")

    new_branch_ref = repo.get_git_ref(ref=f"heads/{branch_name}")
    new_branch_ref.edit(commit.sha)

    print(f"Updated branch {new_branch}")

    try:
        pr_title = f"COLT ./- Generated code library - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        pr_body = "C# classes with namespaces generated from ontologies."
        pr = repo.create_pull(
            title=pr_title, body=pr_body, head=branch_name, base=default_branch.name
        )
    except GithubException as ex:
        print(f"Failed to create pull request: {ex}")
