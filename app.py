from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gemini import ParseSyllabus
from fastapi import File, UploadFile, Form
import io
import pdfplumber
import tasks

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

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