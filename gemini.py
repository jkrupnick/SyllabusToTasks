import tasks
import json
from datetime import datetime
from datetime import timezone

from googleapiclient.errors import HttpError
import google.generativeai as genai




def ParseSyllabus(syllabus, apikey):
    creds = tasks.getCredentials()
    service = tasks.getService(creds) #instance of service
    current_year = datetime.now().year
    

    try:
        #check if token.json is created.
        tasks.getCredentials() #google login 
        api_key = apikey.strip()
        syllabus = syllabus.strip()
        genai.configure(api_key=api_key) #create gemini client
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        prompt = f"""
        Parse the following syllabus text and extract ONLY the assignments, exams, quizzes, projects, and readings mentioned.

        Return a JSON array where each object has:
        - "title": the assignment/exam/reading name
        - "due": the due date in ISO 8601 format (YYYY-MM-DDTHH:MM:00.000Z) OR null

        Inclusions:
        - Include graded assignments, quizzes, tests, exams, projects.
        - Include readings (e.g., "Read Chapter 3", "Article: Smith (2019)").
        - Include other clearly described tasks that have due dates or are associated with a particular class session or date.

        Exclusions:
        - Do NOT include generic course policies, grading breakdowns, or office hours.
        - Do NOT include lecture topics unless they are also explicitly described as assignments, exams, or readings.

        Date rules:
        - If a month and day are given but no year, use the current year: {current_year}.
        - If a year is explicitly given, use that year instead of {current_year}.
        - If a specific calendar date (day + month, with at least an implied year) is NOT clearly provided,
        you MUST set "due" to null.
        - You are NOT allowed to infer or guess a date based on academic schedules,
        end-of-semester conventions, or default dates like December 31.
        - Do NOT convert weeks, module numbers, or sequence labels (e.g., "Week 3 Assignment")
        into dates unless a specific calendar date is explicitly given.

        Time rules:
        - If a time of day is specified, convert it to 24-hour format and use UTC.
        - If no time is provided, set the time to 00:00:00.000Z (start of day).

        Output format:
        - Return ONLY a JSON array.
        - Each element MUST be an object with exactly these keys:
        - "title": string
        - "due": string in ISO 8601 format (YYYY-MM-DDTHH:MM:00.000Z) OR null
        - Do NOT include any other keys.
        - Do NOT include any text before or after the JSON.

        Syllabus text:
        {syllabus}
        """
        
        response = model.generate_content(prompt)
        parsed = json.loads(response.text.strip().replace('```json','').replace('```',''))
        print(json.dumps(parsed, indent=2))
        for task in parsed:
            #normalize title
            task['title'] = task.get('title')
            #validate due date
            due = task.get('due')
            if due:
                try:
                    #throws exception if model messes up date
                    dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
                    task['due'] = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:00.000Z')
                except Exception:
                    task['due'] = None
            else:
                task['due'] = None
        return parsed
        # created = []
        # failed = []
        # for task in parsed:
        #     title = task.get('title', 'Untitled')
        #     try:
                
        #         due = task.get('due')

        #         if due:
        #             dt = datetime.fromisoformat(due.replace('Z', '+00:00'))
        #             due = dt.astimezone(timezone.utc).strftime('%Y-%m-%dT%H:%M:00.000Z')
        #         result = tasks.addTask(service, title=title, due=due)
        #         created.append(result)
        #     except Exception as e:
        #         failed.append({
        #             "title": title,
        #             "error": str(e)
        #         })
        #         print(f"Failed to create task '{title}': {e}")
        # return {"created": created, "failed": failed}
    except HttpError as err:
        print("Google api error" + err)
        return parsed