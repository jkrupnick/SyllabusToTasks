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
        prompt = prompt = f'''Parse the following syllabus text and extract ONLY the assignments/exams mentioned.
        Return a JSON array where each object has:
        - "title": the assignment/exam name
        - "due": the due date in ISO 8601 format (YYYY-MM-DDTHH:MM:00.000Z)

        Important:
        - ONLY include items actually mentioned in the syllabus
        - Use the current year {current_year} unless specified otherwise
        - Convert times to 24-hour format
        - Use UTC timezone
        - If a due date is not clearly stated, set "due" to null instead of guessing
        - Do not invent dates like December 31 when the syllabus is unclear

        Syllabus text:
        {syllabus}

        Return ONLY the JSON array, no explanation.'''
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