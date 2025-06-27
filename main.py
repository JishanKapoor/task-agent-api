import requests
from fastapi import FastAPI, HTTPException
import os
from functions import *
import subprocess

# ✅ Get from Azure App Service Environment Settings
AIPROXY_TOKEN = os.getenv("AIPROXY_TOKEN")

if not AIPROXY_TOKEN:
    raise RuntimeError("AIPROXY_TOKEN is not set in environment variables.")

app = FastAPI()

### /read endpoint
@app.get("/read")
async def read_file(path: str):
    if not path.startswith("/data"):
        raise HTTPException(status_code=403, detail="Access to file is not allowed")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(path, "r") as file:
        content = file.read()
    return {"content": content}

### /run endpoint
@app.post("/run")
async def run_task(task: str):
    try:
        task_output = get_task_output(AIPROXY_TOKEN, task)
        task = task.lower()
        days = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        if "count" in task:
            for day in days:
                if day in task:
                    day = extract_dayname(task)
                    count_days(day)
        elif "install" in task:
            pkgname = extract_package(task)
            correct_package = get_correct_pkgname(pkgname)
            if correct_package:
                subprocess.run(["pip", "install", correct_package])
        else:
            return {"status": "Task is recognized but not implemented yet"}

        return {"status": "success", "task_output": task_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
