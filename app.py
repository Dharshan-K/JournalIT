from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from gitingest import ingest_async
import requests
from dotenv import load_dotenv
from collections import defaultdict
import os
import httpx
import base64
from datetime import datetime
import pymongo
from pymongo.errors import ConnectionFailure
import bcrypt

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173"
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

# @app.on_event("startup")
# async def checkConnection():
#     print("checking connection")
#     try:
#         client.admin.command('ping')
#         print("MongoDB connected")
#     except ConnectionFailure as e:
#         print("MongoDB connection failed")


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
            answer = constructJSON(response.json())
            results = []
            for repo, events in answer.items():
                if(repo == "Dharshan-K/JournalIT"):
                    summary, tree, content = await ingest_async(f"https://github.com/{repo}", exclude_patterns=excludeFiles)
                    model = getModel(summary)
                    print("model used", model)
                    prompt = f"""
                    You are an AI assistant tasked with generating a journal based on GitHub events. 

                    Repository Name: {repo}

                    Repository Structure:
                    {tree}

                    Repository Content:
                    {content}

                    Below are the GitHub events related to this repository:
                    {events}

                    Generate a journal entry summarizing these events in a structured and informative manner.
                    """
                    headers1 = {"Content-Type": "application/json"}
                    data = {"contents": [{"parts": [{"text": prompt}]}]}

                    # response1 = await client.post(
                    #     f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key=AIzaSyCO5sM2nDSKZnDlT6QkGQSk5qMOFamE5u8",
                    #     headers=headers1,
                    #     json=data
                    # )
                    # results.append(response1.json())
            return results

        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=400, detail=f"API request failed: {str(e)}")


def constructJSON(payload):
    categorized_data = defaultdict(lambda: defaultdict(list))
    
    for event in payload:
        repo_name = event["repo"]["name"]
        event_type = event["type"]
        categorized_data[repo_name][event_type].append(event)
    
    print("events data", categorized_data["antiwork/gumroad"])
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
    print(tokens)
    model = ""
    if(tokens>1000000):
        model = "gemini-2.0-flash-thinking-exp-01-21"
    elif(tokens<500000):
        model = "gemini-1.5-flash-001"
    else:
        model = "gemini-2.0-flash"    
    return model

# def verifyRepoStatus(repoOwner):


# def updateIndex(repoName, repoOwner, gitHubToken, currentTime, user, userEmail):    
#     url = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents/index.html"
#     fileUrl = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents/index.html"
#     headers = {
#     "Authorization": f"Bearer {gitHubToken}",
#     "Accept": "application/vnd.github+json"
#     }
#     indexFile = requests.get(url, headers=headers)

#     data={
#         "message" : f"Add journal for {currentTime}",
#         "committer" : {"name" : user, "email" : userEmail},
#         "content" : {"message":f"updated to add {currentTime} entry","committer":{"name":user,"email":userEmail},"content":"bXkgdXBkYXRlZCBmaWxlIGNvbnRlbnRz","sha":"95b966ae1c166bd92f8ae7d1c313e738c731dfc3"}
#     }   

#     return 0

# def contructIndexFile(gitHubToken, repoOwner, repoName):
#     fileUrl = f"https://api.github.com/repos/{repoOwner}/{repoName}/contents/index.html"
#     headers = {
#     "Authorization": f"Bearer {gitHubToken}",
#     "Accept": "application/vnd.github+json"
#     }
#     indexFile = requests.get(fileUrl, headers=headers)


