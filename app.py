from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
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
import json

load_dotenv()

app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://journal-it-eight.vercel.app",
    "https://journalit-1.onrender.com"
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
REDIRECT_URI = "http://127.0.0.1:8000/getOauthUserToken"
@app.get("/")
def run_root():
    return {"message": "hello from FastAPI"}


@app.post("/signUp")
async def userSignIn(userData: Request):
    body = await userData.json()
    password = body['password']    
    user = user_collection.find_one({"userName" :body['userName']})
    if user:
        print("User already exist")
        return {"message" : "User already exist"}
        raise HTTPException(status_code=404, detail="User already exist")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    user_collection.insert_one({"userName":body['userName'], "lastUpdated": None, "password":hashed.decode('utf-8')})    
    verifyUser = user_collection.find_one({"userName" :body['userName']})
    if not verifyUser:
        print("Sign In failed")
        return {"message" : "Sign In failed"}
        raise HTTPException(status_code=404, detail="Failed to signUp")
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
        "lastUpdated": user["lastUpdated"]
    }

@app.get("/getUserAccessToken")
def getUserAccessToken(code: str, state: str):
    print("code",code)
    print(os.getenv('GITHUB_CLIENT_ID'),os.getenv('GITHUB_CLIENT_SECRET'))
    payload = {
        "client_id": os.getenv('GITHUB_CLIENT_ID'),
        "client_secret": os.getenv('GITHUB_CLIENT_SECRET'),
        "code": code
    }
    url = "https://github.com/login/oauth/access_token"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json=payload)
    print(response.json())
    return response.json()

@app.get("/events")
async def getCommits(code: str):
    print("code",code)
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
            answer = constructJSON(response.json(),code)
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
                timeout=60.0
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
    elif(result["Estimated tokens"][-1] == "k"):
        tokens = float(result["Estimated tokens"][:-1]) * 1000
    else:
        tokens = float(result["Estimated tokens"][:-1])
    tokens = float(result["Estimated tokens"][:-1]) * 1000
    model = ""
    if(tokens>1000000):
        model = "gemini-2.0-flash-thinking-exp-01-21"
    elif(tokens<500000):
        model = "gemini-1.5-flash-001"
    else:
        model = "gemini-2.0-flash"  
    return model

@app.post("/commitJournal")
async def commitJournal(journalData: Request):
    body = await journalData.json()
    repoStatus = checkRepo(body['userName'], f"{body['userName']}-Journal", body["token"])
    repoName = body['userName'] + "-Journal"
    headers = {
        "Authorization": f"Bearer {body['token']}",
        "Accept": "application/vnd.github+json"
    }
    fileName = datetime.now().strftime("%d-%m-%Y") + ".html"
    if repoStatus == True:                
        fileContent = base64.b64encode(body['journal'].encode("utf-8")).decode("utf-8")
        fileUrl = f"https://api.github.com/repos/{body['userName']}/{repoName}/contents/{fileName}"
        fileData = {"message":f"{fileName} entry.", "committer":{"name":body['userName'],"email":body['email']},"content":fileContent}
        fileResponse = requests.put(fileUrl, headers=headers, json=fileData)
        print("fileResponse",fileResponse.json())
        constructIndex(body['userName'], f"{body['userName']}-Journal", headers, fileName, body['email'])
        return fileResponse.json()    
    else:
        repoUrl = f"https://api.github.com/user/repos"
        repoData = {"name":repoName,"description":f"{body['userName']}'s Journal.","private":False}
        response = requests.post(repoUrl, headers=headers,json=repoData)
        if response.status_code == 201:
            entryUrl = f"https://api.github.com/repos/{body['userName']}/{repoName}/contents/entry.json"
            jsonContent = returnJSON(repoName, body['userName'], body['email'], fileName)
            entryData = {"message":f"{fileName} entry.", "committer":{"name":body['userName'],"email":body['email']},"content":jsonContent}
            entryResponse = requests.put(entryUrl, headers=headers, json=entryData)
            if entryResponse.status_code == 201:
                indexUrl = f"https://api.github.com/repos/{body['userName']}/{repoName}/contents/index.html"
                indexContent = returnIndex()
                indexData = {"message":"Index.html created.", "committer":{"name":body['userName'],"email":body['email']},"content":indexContent}
                indexResponse = requests.put(indexUrl, headers=headers, json=indexData)
                if indexResponse.status_code == 201:
                    fileContent = base64.b64encode(body['journal'].encode("utf-8")).decode("utf-8")
                    fileUrl = f"https://api.github.com/repos/{body['userName']}/{repoName}/contents/{fileName}"
                    fileData = {"message":f"{fileName} entry.", "committer":{"name":body['userName'],"email":body['email']},"content":fileContent}
                    fileResponse = requests.put(fileUrl, headers=headers, json=fileData)
                else:
                    return {
                        "message": "index.html file not created",
                        "response": indexResponse.json()
                    }
            else:
                return {
                    "message": "Entry.json file not created",
                    "response": entryResponse.json()
                }
        else:
            return {
                "message": "Entry.json file not created",
                "response": response.json()
            }
        return {
            "message":"Your Journal pushed to github.",
            "status" : "false"
        }

def constructIndex(userName, repoName,headers,fileName,email):
    firstLine = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Your Journals</title>
</head>
<body>
<h1>Below are your Journals</h1>
        """
    entryUrl = f"https://api.github.com/repos/{userName}/{repoName}/contents/entry.json"
    response = requests.get(entryUrl, headers=headers)
    print("EntryResponse", response.json())
    if(response.status_code != 201):
        return {
            "message" : "Error retrieving entry.json",
            "status" : response.json()
        }
    data= response.json()
    encoded_content = data["content"]
    decoded_bytes = base64.b64decode(encoded_content)
    json_content = json.loads(decoded_bytes.decode("utf-8"))
    print("Entry.json",json_content)
    json_content["entries"][fileName[:-5]] = fileName
    json_str = json.dumps(json_content)
    jsonContent = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    entryUpdateUrl = f"https://api.github.com/repos/{userName}/{repoName}/contents/entry.json"
    entryData = {"message":f"{fileName[:-5]} entry updated.","committer":{"name":userName,"email":email},"content":jsonContent,"sha": data["sha"]}
    entryUpdateResponse = requests.put(entryUpdateUrl, headers=headers, json=entryData)
    if(response.status_code != 201):
        return {
            "message" : "Error updating entries",
            "status" : entryUpdateResponse.json()
        }
    print("entryUpdateResponse", entryUpdateResponse.json())
    entryUpdateData = entryUpdateResponse.json()
    print("entrysha", entryUpdateData['content']['sha'])
    indexFile = firstLine  + "<ul>\n"
    entries = json_content["entries"]
    for key,value in entries.items():
        value = f"""<li><a href="{fileName}">{key}</a></li>\n"""
        indexFile = indexFile + value
    indexFile = indexFile+ "</ul>\n" + "</body>\n</html>"
    indexFileUrl = f"https://api.github.com/repos/{userName}/{repoName}/contents/index.html"
    indexFileResponse = requests.get(indexFileUrl, headers=headers)
    if(response.status_code != 201):
        return {
            "message" : "Error retrieving index.html",
            "status" : indexFileResponse.json()
        }
    indexData = indexFileResponse.json()
    print("indexData", indexData)
    indexFileSha = indexData['sha']
    indexUpdateUrl = f"https://api.github.com/repos/{userName}/{repoName}/contents/index.html"
    indexupdateContent = base64.b64encode(indexFile.encode("utf-8")).decode("utf-8")
    indexUpdateData = {"message":"index.html updated.","committer":{"name":userName,"email":email},"content":indexupdateContent,"sha": indexFileSha}
    indexUpdateResponse = requests.put(indexUpdateUrl, headers=headers,json=indexUpdateData)
    if(response.status_code != 201):
        return {
            "message" : "Error updating index.html",
            "status" : response.json()
        }
    print("indexUpdateResponse", indexUpdateResponse.json())
    return {
        "message" : "Journal updated.",
        "response" : indexUpdateResponse.json()
    }


def returnIndex():
    firstLine = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Your Journals</title>
</head>
<body>
<h1>Below are your Journals</h1>
</body>
</html>
    """
    indexContent = base64.b64encode(firstLine.encode("utf-8")).decode("utf-8")
    return indexContent

def returnJSON(repoName, userName, email, fileName):
    entryJson = {        
        "repoName": f"{repoName}",
        "entries": {
            fileName[:-5] : fileName,
        },
        "user": {
            "username": f"{userName}",
            "email": f"{email}"
        }        
    }
    json_str = json.dumps(entryJson)
    jsonContent = base64.b64encode(json_str.encode("utf-8")).decode("utf-8")
    return jsonContent

def checkRepo(userName,repoName, token):
    print(repoName)
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }
    repoUrl = f"https://api.github.com/users/{userName}/repos"
    response = requests.get(repoUrl, headers=headers)
    for repo in response.json():
        print(repo['name'])
        if repo['name']==repoName:
            return True
    return False
