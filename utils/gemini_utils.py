import os
import json
import asyncio
import google.generativeai as genai
from fastapi.responses import StreamingResponse
from fastapi import Response
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API"))

DEFAULT_MODEL = "gemini-2.0-flash"

async def generate_response_stream(prompt, character_name=None, model=DEFAULT_MODEL):
    try:
        model_instance = genai.GenerativeModel(model)
        
        input_tokens = model_instance.count_tokens(prompt).total_tokens
        
        if character_name:
            system_prompt = f"You are {character_name}. Respond in the style, personality, and knowledge of {character_name}. Keep responses concise and in-character."
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            
            input_tokens = model_instance.count_tokens(full_prompt).total_tokens
            
            chat = model_instance.start_chat(history=[])
            gemini_response = chat.send_message(full_prompt, stream=True)
        else:
            gemini_response = model_instance.generate_content(prompt, stream=True)
        
        queue = asyncio.Queue()
        
        async def process_response():
            collected_text = []
            
            try:
                for chunk in gemini_response:
                    if chunk.text:
                        collected_text.append(chunk.text)
                        await queue.put(chunk.text)
                
                output_text = "".join(collected_text)
                output_tokens = len(output_text.split()) // 3  
                
                metadata = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }
                
                await queue.put(f"\n__USAGE_METADATA__:{json.dumps(metadata)}")
            finally:
                await queue.put(None)
        
        asyncio.create_task(process_response())
        
        async def stream_generator():
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                yield chunk
        
        response = StreamingResponse(stream_generator(), media_type="text/plain")
        response.headers["X-Input-Tokens"] = str(input_tokens)
        
        return response
        
    except Exception as e:
        print(f"Error generating streamed response: {str(e)}")
        return StreamingResponse(
            iter([f"Sorry, I encountered an error: {str(e)}"]),
            media_type="text/plain"
        )