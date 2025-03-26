from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv;
import os
import httpx
import jsons
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from llama_cpp import Llama
load_dotenv();
app = FastAPI();

origins = [
	"http://localhost:5173"
]

app.add_middleware(
	CORSMiddleware,
	allow_origins = origins,
	allow_credentials = True,
	allow_methods = ["*"],
	allow_headers = ["*"],
)

model_path = "phi-2.Q4_K_M.gguf"
llm = Llama(
    model_path=model_path,
    n_ctx=2048,        
    n_threads=2,      
    n_batch=256,       
    verbose=False
)

@app.get("/")
def run_root():
	return {"message" : "hellow from fast API"}

@app.get("/getUserAccessToken")
def getUserAccessToken(code: str, state:str):
	payload = {
		"client_id" : os.getenv('GITHUB_CLIENT_APP_ID'),
		"client_secret" : os.getenv('GITHUB_CLIENT_APP_SECRET'),
		"code" : code,
		"scope" : "public_repo"
	}
	url = "https://github.com/login/oauth/access_token"
	headers = {
		"Accept":"application/json",
		"Content-Type": "application/json"
	}
	response = requests.post(url, headers=headers, json=payload);
	return response.json()

@app.get("/events")
async def getCommits(code: str):
	print(code)
	url = "https://api.github.com/users/Dharshan-K/events"
	headers = {
		"Authorization" : f"Bearer {code}",
		"Content-Type" : "application/json",
		"Accept" : "application/vnd.github+json"
	}
	response = requests.get(url, headers=headers)
	data = response.json();	
	answer = constructJSON(data)	
	print(model_fn(answer))
	return response.json()

def constructJSON(payload):
	answer = {}
	events = []
	for data in payload:
		if(data["type"] == "PushEvent"):
			for content in data["payload"]["commits"]:				
				entry = {}
				entry["sha"] = content["sha"]
				entry["author"] = content["author"]["name"]
				entry["url"] = content["url"]
				entry["description"] = content["message"]
				events.insert(0,entry)
		answer[data["repo"]["name"]] = events
	return answer

def model_fn(answer):
    try:
        response = llm.create_chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512,
            stop=["</s>"]
        )
        return {"entry": response['choices'][0]['message']['content']}
    except Exception as e:
        return {"error": str(e)}
