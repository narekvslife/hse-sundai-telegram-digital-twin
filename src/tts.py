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

    def synthesize_speech(self, text: str, query_id: str) -> dict:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для синтеза
            query_id: id запроса
            
        Returns:
            Аудио данные в формате WAV
            id запроса
            
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
                    'audio': wav,
                    'query_id': query_id
                   }
        except Exception as e:
            logger.error(f"Ошибка при синтезе речи: {e}")
            raise


if __name__ == "__main__":
    engine = TTSEngine()

    sample_text = "Когда мне было шесть лет, я увидел однажды удивительную картинку."     # текст запроса
    query_id = str(uuid.uuid4())                                                          # id запроса

    res = engine.synthesize_speech(sample_text, query_id)
    
    audio, query_id = res['audio'], res['query_id']
    
    Audio(audio, rate=24000)

