import os
import subprocess
import requests
from fastapi import FastAPI, HTTPException

from functions import *

# ✅ Load from Azure App Service Configuration
API_KEY = os.getenv("API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")

if not API_KEY or not SECRET_KEY:
    raise RuntimeError("API_KEY and/or SECRET_KEY environment variables are not set.")

app = FastAPI()

@app.get("/read")
async def read_file(path: str):
    if not path.startswith("/data"):
        raise HTTPException(status_code=403, detail="Access to file is not allowed")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    with open(path, "r") as file:
        content = file.read()
    return {"content": content}

@app.post("/run")
async def run_task(task: str):
    try:
        task_output = get_task_output(API_KEY, task)
        task = task.lower()
        days = {
            "monday": 0, "tuesday": 1, "wednesday": 2,
            "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6
        }

        if "count" in task:
            for day in days:
                if day in task:
                    extracted_day = extract_dayname(task)
                    count_days(extracted_day)
                    break
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

# ✅ Safe startup
if __name__ == "__main__":
    try:
        import uvicorn
    except ImportError:
        print("uvicorn not found. Installing...")
        subprocess.run(["pip", "install", "uvicorn"])
        import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
