"""
Renderizador de Áudio Lo-Fi
Converte arquivos MIDI em WAV usando FluidSynth e SoundFonts.
"""

import os
import subprocess
import logging

class AudioRenderer:
    def __init__(self, soundfont_path=None):
        # Tenta encontrar o FluidR3_GM que instalamos
        default_sf2 = "/usr/share/sounds/sf2/FluidR3_GM.sf2"
        self.soundfont = soundfont_path if soundfont_path and os.path.exists(soundfont_path) else default_sf2
        
        if not os.path.exists(self.soundfont):
            logging.warning(f"SoundFont não encontrado em {self.soundfont}. A renderização pode falhar.")

    def render(self, midi_path, output_wav_path):
        """
        Renderiza um arquivo MIDI para WAV usando a CLI do FluidSynth.
        """
        if not os.path.exists(midi_path):
            raise FileNotFoundError(f"Arquivo MIDI não encontrado: {midi_path}")

        print(f"Renderizando {midi_path} usando SoundFont: {os.path.basename(self.soundfont)}...")
        
        # Comando para renderização offline (fast-render)
        command = [
            "fluidsynth",
            "-ni",                # Sem interface gráfica
            "-F", output_wav_path, # Arquivo de saída
            "-r", "44100",        # Sample rate
            self.soundfont,
            midi_path
        ]

        try:
            # Executa o processo e captura a saída
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"✓ Renderização concluída: {output_wav_path}")
            return output_wav_path
        except subprocess.CalledProcessError as e:
            print(f"✗ Erro na renderização do FluidSynth: {e.stderr}")
            raise e

if __name__ == "__main__":
    # Teste simples
    renderer = AudioRenderer()
    print(f"Renderer inicializado com SF2: {renderer.soundfont}")
