from dotenv import load_dotenv

load_dotenv()

import os
import openai
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.getenv("OPENAI_API_KEY")

PROMPT = """
You are a helpful assistant only capable of communicating with valid JSON, and no other text.

ONLY return a valid JSON object (no other text is necessary). Be correct and concise.

Here is an example of simple JSON objects that show the expected behavior:
{
    "topics_description": "Here you should define all must-study topics connected to the topic the user wants to sharpen. At least 10 topics should be defined.",
    "topic_list": [
        {
            "topic": "Derivatives",
            "description": "the instantaneous rate of change of a function with respect to another variable.",
            "connected_topics": [
                {
                    "topic": "Limits"
                }
            ]
        },
        {
            "topic": "Limits",
            "description": "In Mathematics, a limit is defined as a value that a function approaches the output for the given input values.",
            "connected_topics": [
                {
                    "topic": "Derivatives"
                },
                {
                    "topic": "Integrals"
                }
            ]
        },
        {
            "topic": "Integrals",
            "description": " a mathematical object that can be interpreted as an area or a generalization of area.",
            "connected_topics": [
                {
                    "topic": "Limits"
                }
            ]
        },
    ]
}

topic_list should contain at least 10 topics. This'll help user study further.
Here is the topic the user wants to sharpen: %s
"""


class InputText(BaseModel):
    input_text: str


@app.post("/get_graph")
async def get_graph(input_data: InputText):
    print("Getting suggestion for: ", input_data.input_text)
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": PROMPT % input_data.input_text,
                },
            ],
        )
        response_message = response["choices"][0]["message"]["content"]

        print(response_message)
        return response_message

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/get_graph_mock")
async def get_graph_mock(input_data: InputText):
    print("Getting suggestion for: ", input_data.input_text)
    try:
        return {
            "topics_description": "The suggested AWS architecture for a video streaming app consists of three main components: storage, processing, and delivery. For storage, Amazon S3 can be used to store the video files. For processing, AWS Lambda can be used to transcode the videos into different formats and resolutions using Amazon Elastic Transcoder. For delivery, Amazon CloudFront can be used as a content delivery network (CDN) to distribute the videos to users with low latency. Additionally, Amazon API Gateway and AWS App Runner can be used to create and manage APIs for the app, while Amazon VPC can be used to set up a secure and isolated network environment with subnets and VPNs.",
            "topic_list": [
                {
                    "topic": "Amazon S3",
                    "description": "Stores the video files",
                    "connected_topics": [{"topic": "AWS Lambda"}],
                },
                {
                    "topic": "AWS Lambda",
                    "description": "Transcodes videos into different formats and resolutions using Amazon Elastic Transcoder",
                    "connected_topics": [{"topic": "Amazon Elastic Transcoder"}],
                },
                {
                    "topic": "Amazon Elastic Transcoder",
                    "description": "Transcodes videos for adaptive streaming",
                    "connected_topics": [{"topic": "Amazon CloudFront"}],
                },
                {
                    "topic": "Amazon CloudFront",
                    "description": "Delivers videos to users with low latency",
                },
                {
                    "topic": "Amazon API Gateway",
                    "description": "Creates and manages APIs for the app",
                    "connected_topics": [{"topic": "AWS App Runner"}],
                },
                {
                    "topic": "AWS App Runner",
                    "description": "Runs the app and manages its deployment",
                },
                {
                    "topic": "Amazon VPC",
                    "description": "Sets up a secure and isolated network environment with subnets and VPNs",
                },
            ],
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
