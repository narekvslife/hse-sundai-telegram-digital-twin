from TTS.api import TTS
import torch
from pathlib import Path
import logging
from IPython.display import Audio
import uuid
import io
from pydub import AudioSegment
from scipy.io.wavfile import write
import numpy as np

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
        Синтез речи и преобразование в OGG
        """
        if not self.model:
            self.initialize()

        try:
            # wav = self.model.tts(
            #     text=text,
            #     speaker="Viktor Menelaos",
            #     language="ru",
            #     split_sentences=True
            # )
            wav = self.model.tts(
                text=text,
                speaker_wav=["src/voice/zvonok-osoboy-gosudarstvennoy-vajnosti.wav"],
                language="ru",
                )

            wav_np = np.array(wav)

            wav_bytes_io = io.BytesIO()
            write(wav_bytes_io, rate=24000, data=(wav_np * 32767).astype(np.int16))
            wav_bytes_io.seek(0)

            audio = AudioSegment.from_wav(wav_bytes_io)
            ogg_io = io.BytesIO()
            audio.export(ogg_io, format="ogg", codec="libopus")
            ogg_io.seek(0)

            return {
                'audio': ogg_io.read(),
            }

        except Exception as e:
            logger.error(f"Ошибка при синтезе речи: {e}")
            raise


tts_engine = TTSEngine()


# if __name__ == "__main__":
#     engine = TTSEngine()

#     sample_text = "Однажды Николай Хадзакос нашел тун тун цахура"   # текст запроса

#     res = engine.synthesize_speech(sample_text)
    
#     audio = res['audio']
    
#     # Save file to directory
#     file_name = f"output/{uuid.uuid4()}.ogg"
#     with open(file_name, 'wb') as f:
#         f.write(audio)
    
#     Audio(audio, rate=24000)

