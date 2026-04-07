import google.generativeai as genai
import json
import os

def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)

async def extract_meeting_intelligence(transcript: str):
    """Uses Gemini API to identify decisions and action items from a transcript."""
    prompt = f"""
    Analyze this meeting transcript and extract all DECISIONS and ACTION ITEMS.
    
    A decision is a concrete conclusion or agreement the team reached.
    An action item is a specific task assigned to a person.
    
    Format the output exactly as the following JSON structure:
    {{
      "decisions": [
        {{
          "title": "Short title of decision",
          "desc": "The reasoning/context (why this was decided)",
          "author": "Who proposed or finalized it"
        }}
      ],
      "actionItems": [
        {{
          "title": "Task description",
          "desc": "Context or reason for the task",
          "assignee": "Person responsible",
          "status": "pending"
        }}
      ]
    }}
    
    Return ONLY valid JSON, no markdown formatting blocks.
    
    Transcript:
    {transcript}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        text = response.text
        # Clean up possible markdown wrappers
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        return json.loads(text.strip())
    except Exception as e:
        print(f"Error extracting intelligence: {e}")
        return {
            "decisions": [],
            "actionItems": []
        }
