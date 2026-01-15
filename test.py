import os
from dotenv import load_dotenv
load_dotenv()

import langchain
import langchain_aws
from langchain_aws import ChatBedrock
from langchain_aws import BedrockEmbeddings
 
from langchain_core.messages import HumanMessage

llm = ChatBedrock(
    model_id="openai.gpt-oss-120b-1:0",
    region_name="eu-west-2",
    model_kwargs={
        "max_tokens": 200
    }
)

# embeddings = BedrockEmbeddings(
#     model_id="amazon.titan-embed-text-v2:0",
#     region_name="eu-west-2"
# )


response = llm.invoke([
    HumanMessage(content="Explain what a safeguard model does in one sentence.")
])

print(response.content.partition("</reasoning>")[2].strip())



# vector = embeddings.embed_query("Hello Bedrock embeddings")
# print(vector)
print(langchain_aws.__version__)
