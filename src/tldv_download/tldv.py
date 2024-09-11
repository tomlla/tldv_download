# Original Code:
# https://gist.github.com/akash-gajjar/24fc183f6b25c74750606606f2319d01

from datetime import datetime
from os import system
import requests
import json
import typer
from typing import *

## Please install ffmpeg before running this script and make sure it's in your PATH
## brew install ffmpeg

## download video from tldv.io
##
## 1. Go to https://tldv.io/
## 2. Login
## 3. Go to the meeting you want to download
## 4. Copy the URL of the meeting
## 5. Open the developer tools (F12)
## 6. Go to the network tab
## 7. Refresh the page
## 8. Find the request to https://gw.tldv.io/v1/meetings/64145828ced74b0013d496ce/watch-page?noTranscript=true
## 9. Copy the auth token from the request headers
## 10. Run this script and paste the URL and auth token
## 11. python3 tldv.py

def get_input(meeting_url: Optional[str], auth_token):
    url = meeting_url if meeting_url else input("\n1. Paste the tldv meeting URL(Example: https://tldv.io/app/meetings/XXXXXX):\n")
    meeting_id = url.split("/")[-1]
    print("Found meeting ID: ", meeting_id)

    if not auth_token:
        auth_token = input('\n2. Paste Auth token from Network Tab (with "Bearer "):\n')

    return [meeting_id, auth_token]


def download(meeting_id: str, auth_token: str):
    data = requests.get(
        f"https://gw.tldv.io/v1/meetings/{meeting_id}/watch-page?noTranscript=true",
        headers={
            "Authorization": auth_token,
        },
    )
    response_body = json.loads(data.text)

    meeting = response_body.get("meeting", {})
    name = meeting.get("name", "No name")

    createdAt = meeting["createdAt"]
    print('createdAt:', createdAt)
    date = datetime.strptime(createdAt, "%Y-%m-%dT%H:%M:%S.%fZ")
    normalized_date = date.strftime("%Y-%m-%d-%H-%M-%S")
    filename = f"downloads/{normalized_date}_{name}.mp4"

    source = response_body.get("video", {}).get("source", None)
    command = f'ffmpeg -i {source} -c copy "{filename}"'
    json_filename = f'{filename}.json'

    with open(json_filename, "w") as f:
        f.write(data.text)

    print(command)
    print("Downloading video...")
    system(command)

def main(
    meeting_url: Optional[str] = typer.Option(None),
    auth_token: Optional[str] = typer.Option(None),
):
    [meeting_id, auth_token] = get_input(meeting_url, auth_token)
    download(meeting_id, auth_token)

if __name__ == "__main__":
    typer.run(main)
