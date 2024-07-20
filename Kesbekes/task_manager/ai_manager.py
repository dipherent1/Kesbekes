import os
import google.generativeai as genai
from datetime import datetime, timedelta

# Configure the Gemini API
genai.configure(api_key=os.getenv("GOOGLE_GEMINI_KEY", "AIzaSyDp6kukZW6rp6ovDuIH2ZuhL8bGOykFTa8"))
model = genai.GenerativeModel('gemini-pro')

def get_ai_response(task, user_preferences, upcoming_tasks, current_time):
    tasks_str = "\n".join([f"{task.title} priority {task.priority} difficulty {task.difficulty} at {task.time} on {task.date}" for task in upcoming_tasks])
    productive_hours_str = ", ".join(user_preferences.productive_hours)
    prompt = f"""
    Based on the following user preferences:
    Wake up time: {user_preferences.wake_up_time}
    Sleep time: {user_preferences.sleep_time}
    Productive hours: {productive_hours_str}
    Preferred categories: {', '.join(user_preferences.preferred_categories)}

    Current date and time: {current_time}

    And the following upcoming tasks:
    {tasks_str}

    Analyze this new task:
    {task['title']} priority {task['priority']} difficulty {task['difficulty']} at {task['time']} on {task['date']}

    Is this a good time for this task? If not, suggest top 3 alternative times within the next 7 days.
    """
    response = model.generate_content(prompt)
    return response.text

def analyze_task(task_text, current_time):
    prompt = f"""
    Analyze the following task description and extract the following information:
    - Task title
    - Task description u can make assumption by using context
    - Date and time, return the target time and date only as requested in output, 
    - Priority level (high, medium, low) only answer with (high, medium, low), u can make assumption by using context dont dont add additional information
    - Difficulty level (high, medium, low) only answer with (high, medium, low), u can make assumption by using context dont add additional information
    - Current date and time: {current_time}

    Task: {task_text}

    Return the information in the following format only, dont need explantion or discription:
    Title: [task title]
    Description: [task description]
    Date: [YYYY-MM-DD]
    Time: [HH:MM]
    Priority: [priority level]
    Difficulty: [difficulty level]


    for example
    if Task is - i have an important meeting after 2 hrs and  Current date and time is 1:00 AM july 21

    output: 

    Description: Attend an important meeting
    Date: 2024-07-21
    Time: 03:00
    Priority: High 
    Difficulty: Low 
    """
    response = model.generate_content(prompt)
    lines = response.text.strip().split('\n')
    result = {}
    for line in lines:
        key, value = line.split(': ', 1)
        result[key.lower()] = value
    return result
