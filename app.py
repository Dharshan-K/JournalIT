from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
from collections import defaultdict
import os
import httpx
import base64
from datetime import datetime
import pymongo
import bcrypt
from datetime import timedelta, datetime

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://journal-it-eight.vercel.app",
    "https://journalit-1.onrender.com",
    "https://j-it.netlify.app"
]
client = pymongo.MongoClient(os.getenv('MONGODB_URL'))
userdb = client['UserData']
user_collection = userdb["users"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# models = {
#     "gemini-2.5-pro-preview-03-25":"gemini-2.5-pro-preview-03-25",
#     "gemini-2.0-flash-thinking-exp-01-21":"gemini-2.0-flash-thinking-exp-01-21",
#     "gemini-2.0-flash-lite-001",
#     "gemini-1.5-flash-001"
# }

@app.get("/")
def run_root():
    return {"message": "hello from FastAPI"}

@app.post("/signUp")
async def userSignIn(userData: Request):
    body = await userData.json()
    print(body)
    password = body['password']
    user = user_collection.find_one({"userName" :body['userName']})
    if user:
        print("User already exist")
        return {"message" : "User already exist"}
        raise HTTPException(status_code=404, detail="User already exist")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    user_collection.insert_one({"userName":body['userName'], "repoName":body['repoName'], "lastUpdated": None, "password":hashed.decode('utf-8')})    
    verifyUser = user_collection.find_one({"userName" :body['userName']})
    if not verifyUser:
        print("Sign In failed")
        return {"message" : "Sign In failed"}
        raise HTTPException(status_code=404, detail="Failed to signUp")
    print("Sign In successfull")
    return "Sign In successfull"

@app.post("/login")
async def userLogin(userData: Request):
    print("logging in")
    body = await userData.json()
    password = body['password']
    user = user_collection.find_one({"userName" :body['userName']})
    if not user:
        print("User not found")
        raise HTTPException(status_code=404, detail="User not found")    
    if not bcrypt.checkpw(password.encode('utf-8'), user["password"].encode('utf-8')):
        print("Password not correct")
        raise HTTPException(status_code=404, detail="Password not correct")
    print(user)
    return {
        "message": "login successfull",
        "userName": user["userName"],
        "repoName" : user["repoName"],
        "lastUpdated": user["lastUpdated"]
    }

@app.get("/getUserAccessToken")
def getUserAccessToken(code: str, state: str):
    payload = {
        "client_id": os.getenv('GITHUB_CLIENT_APP_ID'),
        "client_secret": os.getenv('GITHUB_CLIENT_APP_SECRET'),
        "code": code,
        "scope": "public_repo"
    }
    url = "https://github.com/login/oauth/access_token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    return response.json()

@app.get("/events")
async def getCommits(code: str):
    print("code",code)
    excludeFiles = "*.csv, *.xlsx, *.json, *.log, *.tmp, *.cache, *.lock, *.bin, *.exe, *.dll, *.so, *.a, *.pyc, *.class, *.o, *.env, *.env*.example, *.gitignore, package-lock.json, yarn.lock, Pipfile.lock, *.min.js, *.min.css, *.md, *.pdf, *.docx, *.ppt, *.png, *.jpg, *.svg, .vscode/, .idea/, .DS_Store, *.swp, *.swo, *.spec.js, *_test.py, __snapshots__/, debug.log, coverage/"
    url = "https://api.github.com/users/Dharshan-K/events"
    headers = {
        "Authorization": f"Bearer {code}",
        "Content-Type": "application/json",
        "Accept": "application/vnd.github+json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers)
            response.raise_for_status() 
            # print("response", response.json())
            answer = constructJSON(response.json(),code)
            print("prompt", answer)
            results = []
            prompt = f"""
                Generate a developer’s work log that connects code changes to tangible outcomes. For each entry, specify:

                Action Taken (What the developer did—e.g., ‘Added API endpoint’, ‘Connected DB to service’).

                Purpose/Problem Solved (Why it was needed—e.g., ‘To enable mobile app payments’, ‘To fix login failures’).

                Technical Implementation (Key code/files changed with snippets).

                Result (Observable impact—e.g., ‘API now processes 500 RPM’, ‘DB latency reduced by 30%’).
                {answer}
            """
            headers1 = {"Content-Type": "application/json"}
            data = {"contents": [{"parts": [{"text": prompt}]}]}

            response1 = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={os.getenv('GEMINI_API_KEY')}",
                headers=headers1,
                json=data,
                timeout=30.0
            ) 
            return response1.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"API request failed: {str(e)}")


def constructJSON(payload,code):
    categorized_data = defaultdict(lambda: defaultdict(list))
    current_time = datetime.now()
    last_updated = datetime.now() - timedelta(hours=24)
    
    for event in payload:
        event_time = datetime.strptime(event["created_at"], "%Y-%m-%dT%H:%M:%SZ")
        # if(event_time >= last_updated):
        repo_name = event["repo"]["name"]
        event_type = event["type"]
        commit_url = ""
        if(event_type=="PushEvent"):
            commitPrompt = ""
            for commit in event["payload"]["commits"]:
                url = f"https://api.github.com/repos/{event['repo']['name']}/commits/{commit['sha']}"
                headers = {
                    "Authorization": f"Bearer {code}",
                    "Content-Type": "application/json",
                    "Accept": "application/vnd.github+json"
                }
                print("commitURL", url)
                response = requests.get(url,headers=headers)
                result = response.json()
                prompt = f"""
                message: {commit["message"]}
                """
                for file in result['files']:
                    patch = file.get("patch")
                    if patch:
                        filePrompt = f""" 
                        filename:{file["filename"]}
                        code:
                        {patch}
                        """
                        prompt = prompt + filePrompt

                commitPrompt = prompt
                categorized_data[repo_name][event_type].append(commitPrompt)
        else:
            categorized_data[repo_name][event_type].append(event)
    return categorized_data

async def createHtml(fileContent, repoName, repoOwner, gitHubToken):
    todayDate = datetime.today()
    todayDateStr = todayDate.strftime("%d-%m-%Y")
    base64Content = base64.b64encode(fileContent.decode()).encode()
    url = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents/entries/{todayDateStr}.html"
    headers = {
        "Authorization": f"Bearer {gitHubToken}",
        "Accept": "application/vnd.github+json"
    }
    data = {
        "message": f"Add journal entry: {todayDateStr}.html",
        "content": base64Content,
        "branch": "main"
    }

    response = requests.post(url, headers=headers, json=data)
    return response.json()

def getModel(tokenLimit):
    result = {}
    for line in tokenLimit.strip().split("\n"):
        line = line.strip()
        if not line or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip()
    if(result["Estimated tokens"][-1] == "M"):
        tokens = float(result["Estimated tokens"][:-1]) * 1000000
        print("tokenCount", tokens)
    elif(result["Estimated tokens"][-1] == "k"):
        tokens = float(result["Estimated tokens"][:-1]) * 1000
        print("tokenCount", tokens)
    else:
        tokens = float(result["Estimated tokens"][:-1])
        print("tokenCount", tokens)    
    tokens = float(result["Estimated tokens"][:-1]) * 1000
    print("gitingestTokens",tokens)
    model = ""
    if(tokens>1000000):
        model = "gemini-2.0-flash-thinking-exp-01-21"
    elif(tokens<500000):
        model = "gemini-1.5-flash-001"
    else:
        model = "gemini-2.0-flash"  
    return model

