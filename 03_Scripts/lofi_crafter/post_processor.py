"""
Pós-Processador de Áudio Lo-Fi - Versão Mixagem Limpa
Aplica EQ corretivo (High-Pass/Low-Pass) e Gain Staging para texturas "fantasma".
"""

import os
import random
from pydub import AudioSegment
from pydub.effects import normalize

class PostProcessor:
    def __init__(self, rain_dir=None, vinyl_dir=None):
        base_dir = "/home/ubuntu/youtube_automation/03_Scripts/lofi_crafter/client/assets/samples/loops"
        self.rain_dir = rain_dir if rain_dir else os.path.join(base_dir, "rain")
        self.vinyl_dir = vinyl_dir if vinyl_dir else os.path.join(base_dir, "vinyl")

    def apply_eq_filters(self, audio, low_pass=5000, high_pass=150):
        """
        Aplica filtros de EQ para clareza:
        - Low-pass: Corta agudos extremos (vibe nostálgica).
        - High-pass: Limpa o 'lodo' dos graves.
        """
        print(f"Aplicando EQ: High-pass {high_pass}Hz | Low-pass {low_pass}Hz...")
        audio = audio.high_pass_filter(high_pass)
        audio = audio.low_pass_filter(low_pass)
        return audio

    def add_texture_layer(self, audio, layer_type="rain", volume_reduction=-22):
        """
        Adiciona camadas de textura 'fantasma' com EQ corretivo.
        Corta tudo abaixo de 300Hz nas texturas para evitar colisão de graves.
        """
        target_dir = self.rain_dir if layer_type == "rain" else self.vinyl_dir
        if not os.path.exists(target_dir):
            return audio

        files = [f for f in os.listdir(target_dir) if f.endswith(".mp3")]
        if not files:
            return audio
            
        layer_file = os.path.join(target_dir, random.choice(files))
        print(f"Adicionando textura {layer_type} (Volume: {volume_reduction}dB)...")
        
        texture = AudioSegment.from_mp3(layer_file)
        
        # EQ Corretivo na Textura: Corta graves (300Hz) para não sujar o Bass/Kick
        texture = texture.high_pass_filter(300)
        
        # Ganho sutil (Ghost Texture)
        texture = texture + volume_reduction
        
        # Loop para cobrir o áudio
        loops = (len(audio) // len(texture)) + 1
        texture_loop = (texture * loops)[:len(audio)]
        
        return audio.overlay(texture_loop)

    def process(self, input_wav, output_wav):
        print(f"Iniciando Mixagem Lo-Fi: {input_wav}")
        audio = AudioSegment.from_wav(input_wav)
        
        # 1. EQ Corretivo no Mix Principal (Limpa o lodo abaixo de 100Hz e agudos acima de 5k)
        audio = self.apply_eq_filters(audio, low_pass=5000, high_pass=100)
        
        # 2. Camadas Fantasma (Redução de volume agressiva: -22dB a -25dB)
        audio = self.add_texture_layer(audio, "rain", volume_reduction=-25)
        audio = self.add_texture_layer(audio, "vinyl", volume_reduction=-22)
        
        # 3. Normalização e Export
        audio = normalize(audio)
        audio.export(output_wav, format="wav")
        print(f"✓ Mixagem finalizada: {output_wav}")
        return output_wav
