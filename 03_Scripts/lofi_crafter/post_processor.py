"""
Pós-Processador de Áudio Lo-Fi
Aplica filtros, camadas de ruído (chuva/vinil) e efeitos de masterização.
"""

import os
import random
from pydub import AudioSegment
from pydub.effects import normalize

class PostProcessor:
    def __init__(self, rain_dir=None, vinyl_dir=None):
        # Caminhos padrão baseados na estrutura do repositório
        base_dir = "/home/ubuntu/youtube_automation/03_Scripts/lofi_crafter/client/assets/samples/loops"
        self.rain_dir = rain_dir if rain_dir else os.path.join(base_dir, "rain")
        self.vinyl_dir = vinyl_dir if vinyl_dir else os.path.join(base_dir, "vinyl")

    def apply_lofi_filter(self, audio):
        """
        Aplica filtro Passa-Baixa (Low-pass) para abafar o som (Lo-Fi vibe).
        Frequência de corte recomendada: 4000Hz
        """
        print("Aplicando filtro Low-pass (4000Hz)...")
        return audio.low_pass_filter(4000)

    def add_texture_layer(self, audio, layer_type="rain", volume_reduction=-15):
        """
        Adiciona uma camada de textura (chuva ou vinil) em loop.
        """
        target_dir = self.rain_dir if layer_type == "rain" else self.vinyl_dir
        if not os.path.exists(target_dir):
            print(f"⚠ Diretório de {layer_type} não encontrado em {target_dir}. Pulando camada.")
            return audio

        # Escolhe um arquivo aleatório do diretório
        files = [f for f in os.listdir(target_dir) if f.endswith(".mp3")]
        if not files:
            return audio
            
        layer_file = os.path.join(target_dir, random.choice(files))
        print(f"Adicionando camada de {layer_type}: {os.path.basename(layer_file)}...")
        
        texture = AudioSegment.from_mp3(layer_file)
        
        # Ajusta o volume da textura (precisa ser sutil)
        texture = texture + volume_reduction
        
        # Loop da textura para cobrir a duração do áudio principal
        loops = (len(audio) // len(texture)) + 1
        texture_loop = texture * loops
        texture_loop = texture_loop[:len(audio)] # Corta no tamanho exato
        
        # Mistura os áudios (overlay)
        return audio.overlay(texture_loop)

    def process(self, input_wav, output_wav):
        """
        Pipeline completo de pós-produção.
        """
        print(f"Processando {input_wav}...")
        
        # Carrega o áudio principal
        audio = AudioSegment.from_wav(input_wav)
        
        # 1. Filtro Lo-Fi (Passa-Baixa)
        audio = self.apply_lofi_filter(audio)
        
        # 2. Adicionar Camada de Chuva
        audio = self.add_texture_layer(audio, "rain", volume_reduction=-20)
        
        # 3. Adicionar Camada de Vinil
        audio = self.add_texture_layer(audio, "vinyl", volume_reduction=-18)
        
        # 4. Normalização Final (Mastering básico)
        audio = normalize(audio)
        
        # Exporta o resultado final
        audio.export(output_wav, format="wav")
        print(f"✓ Pós-produção concluída: {output_wav}")
        return output_wav

if __name__ == "__main__":
    # Teste de inicialização
    processor = PostProcessor()
    print(f"PostProcessor pronto. Rain: {processor.rain_dir}")
