import os
import logging
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

class SpeechService:
    def __init__(self):
        """Initialize the Speech Service."""
        self.client = None
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "-":
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    async def transcribe_audio_openai_whisper(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using OpenAI's Whisper model.
        
        Args:
            audio_file_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        try:
            if not self.client:
                logger.error("OpenAI client not initialized - API key may be missing")
                return ""
                
            logger.info(f"Transcribing audio file: {audio_file_path}")
            
            with open(audio_file_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file
                )
            return transcript.text
            
        except Exception as e:
            logger.error(f"Error transcribing audio: {str(e)}")
            return ""

    async def transcribe_audio_self_hosted(self, audio_file_path: str) -> str:
        """
        Transcribe audio file to text using a self hosted Whisper model.
        
        Args:
            audio_file_path: Path to the audio file
        
        Returns:
            Transcribed text
        """
        import aiohttp
        
        try:
            logger.info(f"Transcribing audio file with local Whisper model: {audio_file_path}")
            
            # Local Whisper API endpoint
            local_whisper_url = settings.SELF_HOSTED_WHISPER_URL+"/api/v1/transcribe"
            
            # Read the audio file as binary data
            with open(audio_file_path, "rb") as audio_file:
                file_data = audio_file.read()
            
            # Prepare the file for sending
            files = {'file': (os.path.basename(audio_file_path), file_data)}
            
            # Make the API request to the local Whisper service
            async with aiohttp.ClientSession() as session:
                async with session.post(local_whisper_url, data=files) as response:
                    if response.status == 200:
                        result = await response.json()
                        logger.info(f"Local transcription successful. Language: {result.get('language')}, Duration: {result.get('duration')}s")
                        return result.get('text', '')
                    else:
                        error_text = await response.text()
                        logger.error(f"Local Whisper API returned status {response.status}: {error_text}")
                        return ""
        
        except Exception as e:
            logger.error(f"Error transcribing audio with local Whisper model: {str(e)}")
            return ""

# Create a singleton instance
speech_service = SpeechService()