import os
from typing import List, Dict, Any, Union, Iterator
from elevenlabs import generate, voices
from elevenlabs.api import User
from app.config import settings

class ElevenLabsService:
    def __init__(self):
        # Set API key from settings
        os.environ["ELEVEN_API_KEY"] = settings.ELEVEN_LABS_API_KEY
        self.voice_id = settings.VOICE_ID
        self.audio_dir = settings.AUDIO_DIR
        # Create audio directory if it doesn't exist
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)
    
    async def get_voices(self) -> List[Dict[str, Any]]:
        """Get all available voices from ElevenLabs."""
        try:
            if not settings.ELEVEN_LABS_API_KEY:
                return []
            voice_list = voices()
            return [voice.to_dict() for voice in voice_list]
        except Exception as e:
            print(f"Error getting voices: {str(e)}")
            return []
    
    async def text_to_speech(self, text: str, filename: str) -> bool:
        """
        Convert text to speech using ElevenLabs API.
        Args:
            text: The text to convert to speech.
            filename: The filename to save the audio to.
        Returns:
            True if successful, False otherwise.
        """
        try:
            if not settings.ELEVEN_LABS_API_KEY:
                return False
            
            # Generate audio
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_monolingual_v1"
            )
            
            # Save to file directly using open instead of elevenlabs.save
            full_path = os.path.join(self.audio_dir, filename)
            
            # Convert to bytes if it's an iterator
            if isinstance(audio, bytes):
                audio_bytes = audio
            elif isinstance(audio, bytearray):
                audio_bytes = bytes(audio)
            else:  # Iterator
                audio_bytes = b''.join(list(audio))
                
            # Save using standard file operations
            with open(full_path, 'wb') as f:
                f.write(audio_bytes)
                
            return True
        except Exception as e:
            print(f"Error generating speech: {str(e)}")
            return False

# Create a singleton instance
elevenlabs_service = ElevenLabsService()