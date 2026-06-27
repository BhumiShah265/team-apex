from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks 
from fastapi.middleware.cors import CORSMiddleware 
from fastapi.responses import FileResponse 
import os,shutil,uuid

jobs = {}

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_credentials = True,
    allow_origins = ["*"],
    allow_methods = ["*"],
    allow_headers = ["*"],
)
output = "/Users/unknown1/Desktop/🫡🔼/CV/backend/storage/outputs"
upload = "/Users/unknown1/Desktop/🫡🔼/CV/backend/storage/uploads"
os.makedirs(upload, exist_ok=True)
os.makedirs(output,exist_ok = True)

@app.post("/api/upload")
async def upload_video(background_task:BackgroundTasks,file: UploadFile = File(...),):
    job_id = str(uuid.uuid4())
    file_stored = os.path.join(upload,f"{job_id}.mp4")
    file_bytes = await file.read()
    with open(file_stored,'wb') as BYTE:
        BYTE.write(file_bytes)
    
    jobs[job_id] = {"status": "queued", "progress":0}
    def placeholder(job_id):
        pass
    background_task.add_task(placeholder,job_id)

    return {"job_id":job_id,"status":"queued"}

@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code = 404, detail="Job not found")
    else:
        return {"status": jobs[job_id]["status"],"progress":jobs[job_id]["progress"]}

@app.get("/api/splat/{job_id}")
async def get_splat(job_id:str):
   splat_file= os.path.join(output,f"{job_id}.splat")
   if os.path.exists(splat_file):
       return FileResponse(splat_file, media_type = "application/octet-stream")
   else:
       raise HTTPException(status_code=404,detail = "Splat file not found")
       
