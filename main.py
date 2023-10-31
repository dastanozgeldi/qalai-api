from dotenv import load_dotenv

load_dotenv()

import os
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from constants import GRAPH_PROMPT

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")


class InputUser(BaseModel):
    current_state: str
    goal: str
    start_date: str
    end_date: str


class InputTodo(BaseModel):
    topic: str


@app.post('/get_todo')
async def get_todo(input_data: InputTodo):
    print("Getting suggestion for: ", input_data.topic)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": f"You are a helpful AI assistant that can answer any questions about the given topic. Only answer to what's related to the topic, and don't go off-topic. Generate a list of to dos (max. 5) to achieve this goal: {input_data.topic}. Write shortly and be concise with points. Write only a sentence to each todo."
                }
            ]
        )
        response_message = response["choices"][0]["message"]["content"]

        print(response_message)
        return response_message
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_graph")
async def get_graph(input_data: InputUser):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": GRAPH_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"I'm currently in this state: {input_data.current_state}. My goal: {input_data.goal}. I want to achieve this goal by this date: {input_data.end_date}. I started from this date: {input_data.start_date}. Give me a roadmap that plans out my journey to achieve this goal.",
                },
            ],
        )
        response_message = response["choices"][0]["message"]["content"]

        print(response_message)
        return response_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
