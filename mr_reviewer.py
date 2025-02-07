import openai
import requests
import os

# Read OpenAI API key from environment variable
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Model for API requests
model = "text-davinci-003"

# GitLab API endpoint and personal access token
gitlab_url = os.environ.get("GITLAB_URL")
access_token = os.environ.get("GITLAB_ACCESS_TOKEN")
project_id = os.environ.get("GITLAB_PROJECT_ID")

merge_requests_base = f"{gitlab_url}/projects/{project_id}/merge_requests"

# Headers for API requests
headers = {
    "Private-Token": access_token
}

# Get all merge requests for a specific project
mr_url = f"{merge_requests_base}?scope=all&state=opened&author_username=magikid"
mr_response = requests.get(mr_url, headers=headers)
mr_data = mr_response.json()

# Iterate through each merge request
for mr in mr_data:
    print(f"Analyzing merge request {mr['iid']} - {mr['title']}\n")
    # Get the merge request's code changes
    mr_changes_url = f"{merge_requests_base}/{mr['iid']}/changes"
    mr_changes_response = requests.get(mr_changes_url, headers=headers)
    mr_changes_data = mr_changes_response.json()
    code_changes = mr_changes_data['changes']
    # Use the OpenAI API to analyze the code changes

    response = openai.Completion.create(
        engine=model,
        prompt=f"Analyze the following code changes and find issues that need fixing if any. The code changes are in git diff notation, lines starting with - are deleted, lines starting with + are added: {code_changes}",
        max_tokens=500,
    )
    analysis = f"This comment is auto generated by OpenAI {model} : {response['choices'][0]['text']} "

    # Make comment on merge request with the analysis
    comment_url = f"{merge_requests_base}/{mr['iid']}/notes"
    comment_data = {
        "body": analysis
    }
    print(f"{analysis}\n\n")
    # requests.post(comment_url, headers=headers, data=comment_data)

