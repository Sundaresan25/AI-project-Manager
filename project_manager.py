from google import genai

client = genai.Client(api_key="AIzaSyAVNeFdX_Re8LpKyMmOEnJamUtuZuYN9-E")

project = input("Enter project idea: ")

prompt = f"""
You are a Senior Technical Project Manager.

Project: {project}

Provide:
1. Overview
2. Features
3. Tech Stack
4. Database Design
5. API Endpoints
6. Development Roadmap
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=prompt
)

print(response.text)