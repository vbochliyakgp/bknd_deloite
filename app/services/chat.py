import os

from app.config import settings
# from app.models.chat import ChatResponse, Message
from app.services.audio_service import audio_service



# async def get_intro_messages() ->  :
#     """
#     Get pre-recorded intro messages.
#     """
#     messages = []
    
#     # Add first intro message
#     audio_base64_1 = await audio_service.audio_file_to_base64(os.path.join(settings.AUDIO_DIR, "intro_0.wav"))
#     lipsync_data_1 = await audio_service.read_json_transcript(os.path.join(settings.AUDIO_DIR, "intro_0.json"))
#     messages.append(Message(
#         text="Hey dear... How was your day?",
#         audio=audio_base64_1,
#         lipsync=lipsync_data_1,
#         facialExpression="smile",
#         animation="Talking_1"
#     ))
    
#     # Add second intro message
#     audio_base64_2 = await audio_service.audio_file_to_base64(os.path.join(settings.AUDIO_DIR, "intro_1.wav"))
#     lipsync_data_2 = await audio_service.read_json_transcript(os.path.join(settings.AUDIO_DIR, "intro_1.json"))
#     messages.append(Message(
#         text="I missed you so much... Please don't go for so long!",
#         audio=audio_base64_2,
#         lipsync=lipsync_data_2,
#         facialExpression="sad",
#         animation="Crying"
#     ))
    
#     return ChatResponse(messages=messages)
