from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from gemini import ParseSyllabus
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