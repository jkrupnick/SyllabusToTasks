import os 

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/tasks"]

def getCredentials():
    client_id = os.environ["GOOGLE_CLIENT_ID"]
    client_secret = os.environ["GOOGLE_CLIENT_SECRET"]
    refresh_token = os.environ["GOOGLE_REFRESH_TOKEN"]

    if not client_secret or not client_id or not refresh_token:
        raise RuntimeError("Missing Google OAuth environment variables.")
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=client_id,
        client_secret=client_secret,
        scopes=SCOPES,
    )
    creds.refresh(Request())
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

