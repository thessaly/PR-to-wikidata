import base64
from github import Github
from dotenv import load_dotenv
load_dotenv()
import os

def update_csv(row):
    g = Github(os.getenv("GH_TOKEN"))
    # Get the repo
    repo = g.get_user().get_repo("CQD_metals")
    # Get the file
    file = repo.get_contents('test.csv')
    # New data as string
    finalString = ','.join(row)
    finalString = finalString + '\n'
    # New data as bytes
    encodedString = finalString.encode()
    # Get decoded file contents
    content = file.content
    encodedContent = base64.b64decode(content)
    # New content
    new_content = encodedContent + encodedString
    # Creates target branch
    source_branch = 'master'
    target_branch = 'newfeature'
    sb = repo.get_branch(source_branch)
    repo.create_git_ref(ref='refs/heads/' + target_branch, sha=sb.commit.sha)
    path = file.path
    sha = file.sha

    return repo.update_file(path, 'testing pygithub', new_content, sha, branch=target_branch)