import google.generativeai as genai
import json
import os

def configure_gemini(api_key: str):
    genai.configure(api_key=api_key)

async def extract_meeting_intelligence(transcript: str, attendees: str = None):
    """Uses Gemini API to identify decisions and action items from a transcript."""
    
    attendees_context = ""
    if attendees:
        attendees_context = f"\n\n    KNOWN ATTENDEES IN THIS MEETING: {attendees}\n    You should strongly prefer assigning 'Speaker 0', 'Speaker 1', etc., to these specific names using process of elimination from the conversation."
        
    prompt = f"""
    Analyze this meeting transcript and extract all DECISIONS and ACTION ITEMS.{attendees_context}
    
    A decision is a concrete conclusion or agreement the team reached.
    An action item is a specific task assigned to a person.
    
    CRITICAL INSTRUCTION: The transcript has been scrubbed for privacy. Human names are replaced with tokens like <TOKEN_PERSON_1>. 
    You MUST output the exact token (e.g. "<TOKEN_PERSON_1>") in your JSON whenever referencing a person. Do not remove the brackets.

    STEP 1: Infer Speaker Identities. Identify who "Speaker 0", "Speaker 1", etc., actually are using context clues (e.g. if Speaker 1 says "What do you think, <TOKEN_PERSON_2>?" and Speaker 0 answers, Speaker 0 is likely <TOKEN_PERSON_2>). 
    Map every Speaker tag to either their exact <TOKEN_PERSON_X> or their literal real name if it wasn't scrubbed. 
    IF you cannot definitively infer their real name or exact <TOKEN>, you MUST map them to their original generic label (e.g. "Speaker 0"). DO NOT invent placeholder titles like "Meeting Lead", "Participant", or "Host".

    Format the output exactly as the following JSON structure:
    {{
      "speaker_mapping": {{
        "Speaker 0": "Literal Name, exact <TOKEN_PERSON_X>, or 'Speaker 0'",
        "Speaker 1": "Literal Name, exact <TOKEN_PERSON_X>, or 'Speaker 1'"
      }},
      "decisions": [
        {{
          "title": "Short title of decision",
          "desc": "The reasoning/context (why this was decided)",
          "author": "The speaker's identity (e.g. Speaker 0)"
        }}
      ],
      "actionItems": [
        {{
          "title": "Task description",
          "desc": "Context or reason for the task",
          "assignee": "The speaker's identity (e.g. Speaker 1) or exact <TOKEN_PERSON_X>",
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
        data = json.loads(text.strip())
        
        # Apply Speaker Mapping Identifications
        mapping = data.get("speaker_mapping", {})
        for dec in data.get("decisions", []):
            if dec.get("author") in mapping:
                dec["author"] = mapping[dec["author"]]
        for act in data.get("actionItems", []):
            if act.get("assignee") in mapping:
                act["assignee"] = mapping[act["assignee"]]
                
        return data
    except Exception as e:
        print(f"Error extracting intelligence: {e}")
        return {
            "decisions": [],
            "actionItems": []
        }

async def chat_intelligence(message: str, context: dict):
    """Uses Gemini to answer user questions based on the extracted meeting context"""
    prompt = f"""
    You are an AI assistant for a Meeting Intelligence Hub. Answer the user's question about the recent meeting.
    Use the following extracted meeting data (Decisions, Action Items, and Speaker Mappings) to inform your response.
    Be concise, helpful, and speak directly to the user. Do not explain the JSON structure.

    MEETING DATA:
    {json.dumps(context, indent=2)}

    USER QUESTION: {message}
    """
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return {"reply": response.text.strip()}
    except Exception as e:
        print(f"Chat error: {e}")
        return {"reply": "Sorry, I am having trouble answering that right now."}

