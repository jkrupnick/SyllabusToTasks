Created by Jack Krupnick

# SyllabusToTasks
Convert your course syllabus into a Google Tasks list instantly. 

## Problem Solved:
Manually going through a syllabus to extract assignments, due dates, and tasks into Google Tasks is time-consuming and error-prone. SyllabusToTasks automates this process using AI.

## Features:
- Uses Gemini AI to intelligently extract assignments and due dates
- Review and edit tasks before creating them in Google Tasks
- Save directly to your Google Tasks with proper dates and titles
- **Important:** AI parsing can make mistakes with dates and may miss assignments. Always review all tasks carefully on the review page before saving.

## Tech Stack
- **Backend:** Python FastAPI
- **Frontend:** HTML, CSS, Vanilla JavaScript (ES6)
- **AI:** Google Gemini 2.5-flash-lite API
- **PDF Processing** pdfplumber
- **Auth:** Google OAuth 2.0
- **API:** Google Tasks API v1
- **Deployment:** FastAPI + Uvicorn

### Prerequisites
- Google account
- Gemini API key

## Troubleshooting
**"Invalid API key"**
- Get a free key at https://aistudio.google.com/app/api-keys
- Make sure it's pasted correctly (no extra spaces)

**Tasks not appearing in Google Tasks**
- Confirm Google OAuth login succeeded
- Check browser console for errors (F12)
- Verify tasks are in the default tasklist
- AI may have missed a task or incorrectly parsed one. Always review first on the review page

**Dates are wrong**
- Review page lets you edit dates before saving
- Adjust if needed before clicking "Save"
