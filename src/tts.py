from TTS.api import TTS
import torch
from pathlib import Path
import logging

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

    def synthesize_speech(self, text: str, output_filename: str = "output.wav") -> bytes:
        """
        Синтез речи из текста
        
        Args:
            text: Текст для синтеза
            output_filename: Имя выходного файла
            
        Returns:
            bytes: Аудио данные в формате WAV
        """
        if not self.model:
            self.initialize()
            
        try:
            output_path = self.output_dir / output_filename
            wav = self.model.tts(
                text=text,
                file_path=str(output_path),
                speaker="Viktor Menelaos",
                language="ru",
                split_sentences=True
            )
            logger.info(f"Речь успешно синтезирована в файл {output_path}")
            return wav
        except Exception as e:
            logger.error(f"Ошибка при синтезе речи: {e}")
            raise
