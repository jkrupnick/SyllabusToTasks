from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import HTMLResponse
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gemini import ParseSyllabus
from fastapi import File, UploadFile, Form
import io
import os
import pdfplumber
import tasks

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

SCOPES = ["https://www.googleapis.com/auth/tasks"]

class SyllabusRequest(BaseModel): #the input we will need to parse
    syllabus: str
    apikey: str

@app.get("/", response_class=HTMLResponse)
async def root():
    with open("templates/index.html","r")as f:
        return f.read()
    
@app.get("/review",response_class=HTMLResponse)
async def review():
    with open("templates/review.html","r") as f:
        return f.read()
    
@app.get("/confirmation",response_class=HTMLResponse)
async def confirmation():
    with open("templates/confirmation.html","r") as f:
        return f.read()
    
@app.post("/parse-syllabus")
async def parseSyllabus(request: SyllabusRequest):
    parsedJson = ParseSyllabus(request.syllabus,request.apikey)
    return {"tasks": parsedJson}


@app.post('/parse-syllabus-file')
async def parse_syllabus_file(apikey: str = Form(...), file: UploadFile = File(...)):
    # only accept PDFs for now
    try:
        data = await file.read()
        text_parts = []
        # use pdfplumber to extract text from the PDF
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                try:
                    txt = page.extract_text() or ''
                except Exception:
                    txt = ''
                text_parts.append(txt)
        syllabus_text = '\n'.join(text_parts)
    except Exception:
        syllabus_text = ''

    parsedJson = ParseSyllabus(syllabus_text, apikey)
    return {"tasks": parsedJson}

@app.post("/save-tasks")
async def saveTasks(request: dict):
    tasks_to_create = request.get("tasks", [])
    creds = tasks.getCredentials()
    service = tasks.getService(creds)
    created = []
    failed = []
    for task in tasks_to_create:
        title = task.get('title')
        try:
            result = tasks.addTask(service, title=title, due=task.get('due'))
            created.append(result)
        except Exception as e:
            failed.append({"task": task, "error": str(e)})
    return {"created": created, "failed": failed}

@app.get("/authorize")
async def authorize():
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri="https://syllabustotasks.onrender.com/oauth2callback",
    )
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent',
    )
    return RedirectResponse(authorization_url)

@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    flow = Flow.from_client_config(
        {
            "web": {
                "client_id": os.environ["GOOGLE_CLIENT_ID"],
                "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token"
            }
        },
        scopes=SCOPES,
        redirect_uri="https://syllabustotasks.onrender.com/oauth2callback",
    )
    #Redirected here with ?code=
    flow.fetch_token(authorization_response=str(request.url))
    creds = flow.credentials

    refresh_token = creds.refresh_token
    return HTMLResponse(
        f"OAuth Complete. Refresh Token received: {refresh_token}. You can close this window and return to the app."
    )