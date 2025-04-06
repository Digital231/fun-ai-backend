import os
import json
import asyncio
import google.generativeai as genai
from fastapi.responses import StreamingResponse
from fastapi import Response
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API"))

# Default model - you can change this based on your needs
DEFAULT_MODEL = "gemini-2.0-flash"

async def generate_response_stream(prompt, character_name=None, model=DEFAULT_MODEL):
    try:
        model_instance = genai.GenerativeModel(model)
        
        # Get input token count before sending the request
        input_tokens = model_instance.count_tokens(prompt).total_tokens
        
        if character_name:
            system_prompt = f"You are {character_name}. Respond in the style, personality, and knowledge of {character_name}. Keep responses concise and in-character."
            full_prompt = f"{system_prompt}\n\nUser: {prompt}"
            
            # Update token count with the full prompt
            input_tokens = model_instance.count_tokens(full_prompt).total_tokens
            
            chat = model_instance.start_chat(history=[])
            gemini_response = chat.send_message(full_prompt, stream=True)
        else:
            gemini_response = model_instance.generate_content(prompt, stream=True)
        
        # Create a queue to handle the streaming
        queue = asyncio.Queue()
        
        # Create a task to process the response and put chunks into the queue
        async def process_response():
            collected_text = []
            
            try:
                for chunk in gemini_response:
                    if chunk.text:
                        collected_text.append(chunk.text)
                        await queue.put(chunk.text)
                
                # After all chunks, add metadata
                output_text = "".join(collected_text)
                output_tokens = len(output_text.split()) // 3  # Very rough estimate
                
                metadata = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": input_tokens + output_tokens
                }
                
                await queue.put(f"\n__USAGE_METADATA__:{json.dumps(metadata)}")
            finally:
                # Signal that we're done
                await queue.put(None)
        
        # Start the processing task
        asyncio.create_task(process_response())
        
        # Create an async generator for streaming
        async def stream_generator():
            while True:
                chunk = await queue.get()
                if chunk is None:
                    break
                yield chunk
        
        # Create response with token headers
        response = StreamingResponse(stream_generator(), media_type="text/plain")
        response.headers["X-Input-Tokens"] = str(input_tokens)
        
        return response
        
    except Exception as e:
        print(f"Error generating streamed response: {str(e)}")
        return StreamingResponse(
            iter([f"Sorry, I encountered an error: {str(e)}"]),
            media_type="text/plain"
        )