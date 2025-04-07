import os
import json
import base64
import asyncio
import time
from typing import Dict, Any, Tuple
import logging

from app.config import settings

logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self):
        self.audio_dir = settings.AUDIO_DIR
        
        # Create audio directory if it doesn't exist
        if not os.path.exists(self.audio_dir):
            os.makedirs(self.audio_dir)

    async def convert_mp3_to_wav(self, mp3_path: str, wav_path: str) -> bool:
        """
        Convert MP3 file to WAV using ffmpeg.
        
        Args:
            mp3_path: Path to the MP3 file.
            wav_path: Path to save the WAV file.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            start_time = time.time()
            logger.info(f"Starting conversion for {mp3_path}")
            
            # Run ffmpeg command to convert MP3 to WAV
            process = await asyncio.create_subprocess_exec(
                "ffmpeg", "-y", "-i", mp3_path, wav_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Conversion done in {(time.time() - start_time) * 1000:.0f}ms")
                return True
            else:
                logger.error(f"Error converting audio: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Exception in convert_mp3_to_wav: {str(e)}")
            return False

    async def generate_lipsync(self, wav_path: str, json_path: str) -> bool:
        """
        Generate lipsync data using Rhubarb Lip Sync.
        
        Args:
            wav_path: Path to the WAV file.
            json_path: Path to save the JSON lipsync data.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            start_time = time.time()
            
            # Run Rhubarb command to generate lipsync data
            process = await asyncio.create_subprocess_exec(
                "./bin/rhubarb", "-f", "json", "-o", json_path, wav_path, "-r", "phonetic",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                logger.info(f"Lip sync done in {(time.time() - start_time) * 1000:.0f}ms")
                return True
            else:
                logger.error(f"Error generating lipsync: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"Exception in generate_lipsync: {str(e)}")
            return False

    async def process_audio_for_message(self, message_index: int, text: str) -> Tuple[str, Dict[str, Any]]:
        """
        Process audio for a message, including TTS, conversion, and lipsync.
        
        This is a placeholder that would normally call elevenlabs_service.
        
        Args:
            message_index: Index of the message.
            text: Text of the message.
            
        Returns:
            Tuple of (base64_audio, lipsync_data).
        """
        mp3_path = os.path.join(self.audio_dir, f"message_{message_index}.mp3")
        wav_path = os.path.join(self.audio_dir, f"message_{message_index}.wav")
        json_path = os.path.join(self.audio_dir, f"message_{message_index}.json")
        
        # First we'd generate the MP3 using elevenlabs_service
        # This is handled elsewhere
        
        # Then convert MP3 to WAV
        await self.convert_mp3_to_wav(mp3_path, wav_path)
        
        # Generate lipsync data
        await self.generate_lipsync(wav_path, json_path)
        
        # Read audio and lipsync data
        audio_base64 = await self.audio_file_to_base64(mp3_path)
        lipsync_data = await self.read_json_transcript(json_path)
        
        return audio_base64, lipsync_data

    async def audio_file_to_base64(self, file_path: str) -> str:
        """
        Convert audio file to base64 string.
        
        Args:
            file_path: Path to the audio file.
            
        Returns:
            Base64-encoded string of the audio file.
        """
        try:
            with open(file_path, "rb") as audio_file:
                audio_data = audio_file.read()
                return base64.b64encode(audio_data).decode("utf-8")
        except Exception as e:
            logger.error(f"Error reading audio file {file_path}: {str(e)}")
            return ""

    async def read_json_transcript(self, file_path: str) -> Dict[str, Any]:
        """
        Read JSON lipsync transcript.
        
        Args:
            file_path: Path to the JSON file.
            
        Returns:
            JSON lipsync data.
        """
        try:
            with open(file_path, "r") as json_file:
                return json.load(json_file)
        except Exception as e:
            logger.error(f"Error reading JSON file {file_path}: {str(e)}")
            return {}

# Create a singleton instance
audio_service = AudioService()