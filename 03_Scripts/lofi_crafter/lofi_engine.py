"""
Lofi Generator Engine - Motor Principal de Geração de Músicas Lo-Fi
Sistema consolidado: MIDI -> Renderização SF2 -> Pós-Produção (Filtros + Camadas).
"""

import os
import random
import argparse
from typing import Optional, Dict, List
from mido import MidiFile, MidiTrack, MetaMessage, Message
import mido

from midi_generator import LofiMidiGenerator, LofiStyle
from drum_generator import DrumGenerator
from audio_renderer import AudioRenderer
from post_processor import PostProcessor


class LofiEngine:
    """
    Motor principal de geração de músicas Lo-Fi.
    Consolida harmonia, melodia, bateria e masterização em um único fluxo.
    """
    
    STYLE_PRESETS = {
        LofiStyle.CHILLHOP: {
            'name': 'Chillhop',
            'description': 'Piano de feltro, baixos marcados e beats consistentes',
            'bpm_range': (75, 90),
            'key_preferences': ['C', 'F', 'G', 'D'],
            'mode': 'minor',
            'measures': 16,
            'has_drums': True,
        },
        LofiStyle.JAZZHOP: {
            'name': 'Jazzhop',
            'description': 'Progressões jazzísticas complexas com swing acentuado',
            'bpm_range': (80, 95),
            'key_preferences': ['Eb', 'Bb', 'F', 'Ab'],
            'mode': 'dorian',
            'measures': 16,
            'has_drums': True,
        },
        LofiStyle.SLEEP: {
            'name': 'Sleep/Ambient Lo-Fi',
            'description': 'Andamento lento, bateria sutil, acordes sustentados',
            'bpm_range': (60, 70),
            'key_preferences': ['A', 'E', 'D', 'G'],
            'mode': 'minor',
            'measures': 24,
            'has_drums': False,
        },
        LofiStyle.AMBIENT: {
            'name': 'Ambient Lo-Fi',
            'description': 'Atmosférico, foco em texturas e pads',
            'bpm_range': (60, 70),
            'key_preferences': ['A', 'E', 'D'],
            'mode': 'minor',
            'measures': 24,
            'has_drums': False,
        },
        LofiStyle.SAD: {
            'name': 'Sad Lo-Fi',
            'description': 'Progressões em tons menores, melodias melancólicas',
            'bpm_range': (70, 80),
            'key_preferences': ['Am', 'Dm', 'Em', 'Bm'],
            'mode': 'minor',
            'measures': 16,
            'has_drums': True,
        },
        LofiStyle.NOSTALGIC: {
            'name': 'Nostalgic Lo-Fi',
            'description': 'Melodias espaçadas e emotivas, progressões nostálgicas',
            'bpm_range': (70, 80),
            'key_preferences': ['C', 'G', 'D', 'A'],
            'mode': 'minor',
            'measures': 16,
            'has_drums': True,
        },
    }
    
    def __init__(self, output_dir: str = './output'):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.renderer = AudioRenderer()
        self.processor = PostProcessor()
    
    def _parse_key_and_mode(self, key_str: str) -> tuple:
        if key_str.endswith('m'):
            return key_str[:-1], 'minor'
        return key_str, 'major'
    
    def generate_track(self, 
                      style: LofiStyle,
                      key: Optional[str] = None,
                      bpm: Optional[int] = None,
                      measures: Optional[int] = None,
                      include_drums: Optional[bool] = None,
                      filename: Optional[str] = None,
                      render_audio: bool = True) -> str:
        """
        Gera uma faixa Lo-Fi completa (MIDI -> WAV Masterizado).
        """
        preset = self.STYLE_PRESETS[style]
        
        if key is None:
            key_choice = random.choice(preset['key_preferences'])
            key, mode = self._parse_key_and_mode(key_choice)
        else:
            key, mode = self._parse_key_and_mode(key)
        
        if bpm is None:
            bpm_min, bpm_max = preset['bpm_range']
            bpm = random.randint(bpm_min, bpm_max)
        
        if measures is None:
            measures = preset['measures']
        
        if include_drums is None:
            include_drums = preset['has_drums']
        
        if filename is None:
            base_name = f"lofi_{preset['name'].lower().replace('/', '_').replace(' ', '_')}_{key}{mode[0]}_{bpm}bpm"
        else:
            base_name = filename.replace('.mid', '')
            
        midi_path = os.path.join(self.output_dir, f"{base_name}.mid")
        
        # 1. Geração MIDI
        mid = MidiFile(ticks_per_beat=480)
        
        # Track de tempo
        tempo_track = MidiTrack()
        mid.tracks.append(tempo_track)
        tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        tempo_track.append(MetaMessage('time_signature', numerator=4, denominator=4, clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
        
        print(f"Gerando {preset['name']} - Key: {key} {mode}, BPM: {bpm}, Measures: {measures}")
        
        generator = LofiMidiGenerator(key=key, mode=mode)
        generator.bpm = bpm
        prog = random.choice(generator.MELANCHOLIC_PROGRESSIONS)
        
        mid.tracks.append(generator.generate_harmony_track(mid, prog, measures))
        mid.tracks.append(generator.generate_bass_track(mid, prog, measures))
        mid.tracks.append(generator.generate_pad_track(mid, prog, measures))
        mid.tracks.append(generator.generate_melody_track(mid, prog, measures))
        
        if include_drums:
            drum_gen = DrumGenerator(style=style, bpm=bpm)
            mid.tracks.append(drum_gen.generate_drum_track(mid, measures=measures))
            print(f"  ✓ Bateria adicionada com sincronia de grade")
        
        mid.save(midi_path)
        print(f"  ✓ Arquivo MIDI salvo: {midi_path}")
        
        # 2. Renderização de Áudio e Pós-Produção
        if render_audio:
            try:
                # Renderiza MIDI para WAV (Limpo)
                clean_wav = midi_path.replace('.mid', '_clean.wav')
                self.renderer.render(midi_path, clean_wav)
                
                # Pós-processamento (Filtros + Camadas)
                final_wav = midi_path.replace('.mid', '_final_master.wav')
                self.processor.process(clean_wav, final_wav)
                
                # Limpa o arquivo intermediário
                if os.path.exists(clean_wav):
                    os.remove(clean_wav)
                
                print(f"✓ Masterização completa: {final_wav}")
                return final_wav
            except Exception as e:
                print(f"✗ Erro na renderização/pós-produção: {e}")
        
        return midi_path

    def generate_all_styles(self, measures: int = 8) -> List[str]:
        generated_files = []
        print("=" * 60)
        print("GERADOR DE MÚSICAS LO-FI - PIPELINE COMPLETO")
        print("=" * 60)
        for style in LofiStyle:
            print(f"\n[{style.value.upper()}]")
            try:
                filepath = self.generate_track(style=style, measures=measures)
                generated_files.append(filepath)
            except Exception as e:
                print(f"  ✗ Erro ao gerar {style.value}: {e}")
        return generated_files


def main():
    parser = argparse.ArgumentParser(description='Gerador de Músicas Lo-Fi - Pipeline Completo')
    parser.add_argument('--style', type=str, choices=[s.value for s in LofiStyle], help='Estilo de Lo-Fi')
    parser.add_argument('--key', type=str, help='Tonalidade (ex: C, Am)')
    parser.add_argument('--bpm', type=int, help='BPM')
    parser.add_argument('--measures', type=int, default=16, help='Compassos')
    parser.add_argument('--no-drums', action='store_true', help='Sem bateria')
    parser.add_argument('--no-audio', action='store_true', help='Apenas MIDI, sem renderizar áudio')
    parser.add_argument('--output', type=str, default='./output', help='Diretório de saída')
    parser.add_argument('--all', action='store_true', help='Gerar todos os estilos')
    parser.add_argument('--list', action='store_true', help='Listar estilos')
    
    args = parser.parse_args()
    
    if args.list:
        print("\nEstilos de Lo-Fi disponíveis:\n")
        for style, preset in LofiEngine.STYLE_PRESETS.items():
            print(f"  • {preset['name']}: {preset['description']}")
        return
    
    engine = LofiEngine(output_dir=args.output)
    
    if args.all:
        engine.generate_all_styles(measures=args.measures)
        return
    
    if args.style:
        style = LofiStyle(args.style)
        engine.generate_track(
            style=style,
            key=args.key,
            bpm=args.bpm,
            measures=args.measures,
            include_drums=not args.no_drums,
            render_audio=not args.no_audio
        )
    else:
        print("Use --style para especificar um estilo ou --all para gerar todos.")


if __name__ == "__main__":
    main()
