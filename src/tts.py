from TTS.api import TTS
import torch
from pathlib import Path
import logging
from IPython.display import Audio
import uuid


logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)
        
    def initialize(self):
        """Инициализация модели TTS"""
        try:
            self.model = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to(self.device)
            logger.info(f"TTS модель инициализирована на устройстве {self.device}")
        except Exception as e:
            logger.error(f"Ошибка при инициализации TTS модели: {e}")
            raise

    def synthesize_speech(self, text: str) -> dict:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для синтеза
            
        Returns:
            Аудио данные в формате WAV
            
        """
        if not self.model:
            self.initialize()
            
        try:
            wav = self.model.tts(
                text=text,
                speaker="Viktor Menelaos",
                language="ru",
                split_sentences=True
            )
            return {
                    'audio': wav
                   }
        
        except Exception as e:
            logger.error(f"Ошибка при синтезе речи: {e}")
            raise


tts_engine = TTSEngine()


if __name__ == "__main__":
    engine = TTSEngine()

    sample_text = "Когда мне было шесть лет, я увидел однажды удивительную картинку."     # текст запроса

    res = engine.synthesize_speech(sample_text)
    
    audio = res['audio']
    
    Audio(audio, rate=24000)

