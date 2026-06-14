"""
transcrever_simples.py
======================
Transcreve o arquivo audio_padrao.m4a usando apenas o Whisper.

Instale antes de rodar:
    pip install openai-whisper
    (FFmpeg já instalado — ok!)
"""

import whisper
import os

AUDIO_INPUT = r"C:\Users\BrunoAlexandredeCarv\Transcreve\audio_padrao.m4a"
OUTPUT_TXT  = r"C:\Users\BrunoAlexandredeCarv\Transcreve\transcricao.txt"
MODELO      = "medium"  # opções: tiny, base, small, medium, large

print("Carregando modelo Whisper...")
modelo = whisper.load_model(MODELO)

print(f"Transcrevendo '{AUDIO_INPUT}'... (pode demorar alguns minutos)")
resultado = modelo.transcribe(AUDIO_INPUT, language="pt", verbose=True)

with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
    f.write(resultado["text"])

print(f"\nPronto! Transcrição salva em '{OUTPUT_TXT}'")