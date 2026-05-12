import os.path
import json 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
SCOPES = ["https://www.googleapis.com/auth/tasks"]
def getCredentials():
    creds = None
    # Check for stored token
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # Log in 
    if not creds or not creds.valid:
        try:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                raise Exception("No valid refresh token")
        except Exception:
            #force re-auth refresh failed
            if os.path.exists("token.json"):
                os.remove("token.json")
            flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save creds
    
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    #these creds used for building service
    return creds

def getService(creds):
    return build("tasks","v1",credentials=creds)

def addTask(service, tasklist_id='@default', title=None, due=None, task_body=None):
    """Create a task in Google Tasks.

    Args:
        service: authorized Google Tasks service instance
        tasklist_id: id of the tasklist (defaults to '@default')
        title: task title (optional if task_body.provides title)
        due: RFC3339 due string (optional)
        task_body: optional dict to use directly as the task body

    Returns:
        The created task resource (dict) on success.

    Raises:
        ValueError for invalid input, or re-raises HttpError from the API.
    """
    if task_body is None:
        if not title:
            raise ValueError('title is required when task_body is not provided')
        task = {"title": title}
        if due:
            if not isinstance(due, str) or not due.strip():
                raise ValueError('due must be a non-empty RFC3339 string')
            task["due"] = due
    else:
        # shallow copy to avoid mutating caller dict
        task = dict(task_body)
        if title:
            task.setdefault('title', title)
        if due:
            task.setdefault('due', due)
    try:
        return service.tasks().insert(tasklist=tasklist_id, body=task).execute()
    except HttpError as e:
        print(f"Failed to add task to tasklist {tasklist_id}: {e}")
        raise

