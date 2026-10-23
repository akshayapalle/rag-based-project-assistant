import os
from dotenv import load_dotenv
from openai import AzureOpenAI

from project_intelligence import get_project_context


# Load environment variables
load_dotenv()


# Connect to Azure OpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("AOAI_CHAT_ENDPOINT"),
    api_key=os.getenv("AOAI_CHAT_KEY"),
    api_version=os.getenv("AOAI_API_VERSION_GPT")
)


# Get current project information from PostgreSQL
project_context = get_project_context()


print("\n==============================")
print("SHOPSPHERE PROJECT COPILOT")
print("==============================")
print("Ask questions about the project.")
print("Type 'exit' to stop.\n")


# Keep asking questions
while True:

    question = input("You: ")

    # Stop the program
    if question.lower() == "exit":
        print("\nProject Copilot stopped.")
        break

    # Send project context + question to AI
    response = client.chat.completions.create(
        model=os.getenv("AOAI_CHAT_DEPLOYMENT"),
        messages=[
            {
                "role": "system",
                "content": """
You are an AI Project Copilot.

You help a Project Manager understand the current state
of a software project.

Answer questions using ONLY the project context provided.

Important rules:

1. Prefer the most recent information when project updates
   contain older and newer information about the same topic.

2. Distinguish between historical events and the current state.

3. Do not invent information.

4. If the information is not available, clearly say:
   "This information is not available in the project data."

5. Give concise, practical answers suitable for a Project Manager.
"""
            },
            {
                "role": "user",
                "content": f"""
Here is the current project context:

{project_context}

Project Manager's question:

{question}
"""
            }
        ]
    )

    print("\nCopilot:")
    print(response.choices[0].message.content)
    print()