"""
Lofi Generator Engine - Motor Principal de Geração de Músicas Lo-Fi
Sistema modular e consolidado para geração de diferentes estilos de Lo-Fi
"""

import os
import random
from typing import Optional, Dict, List
from mido import MidiFile, MidiTrack, MetaMessage
import mido

from midi_generator import LofiMidiGenerator, LofiStyle
from drum_generator import DrumGenerator


class LofiEngine:
    """
    Motor principal de geração de músicas Lo-Fi
    Consolida harmonia, melodia e bateria em um único fluxo de trabalho
    """
    
    # Configurações de estilo
    STYLE_PRESETS = {
        LofiStyle.CHILLHOP: {
            'name': 'Chillhop',
            'description': 'Foco em samples de piano, baixos marcados e beats consistentes',
            'bpm_range': (75, 90),
            'key_preferences': ['C', 'F', 'G', 'D'],
            'mode': 'major',
            'measures': 16,
            'has_drums': True,
            'drum_intensity': 'medium',
        },
        LofiStyle.JAZZHOP: {
            'name': 'Jazzhop',
            'description': 'Progressões jazzísticas complexas com swing acentuado',
            'bpm_range': (80, 95),
            'key_preferences': ['Eb', 'Bb', 'F', 'Ab'],
            'mode': 'dorian',
            'measures': 16,
            'has_drums': True,
            'drum_intensity': 'medium',
        },
        LofiStyle.SLEEP: {
            'name': 'Sleep/Ambient Lo-Fi',
            'description': 'Andamento lento, bateria sutil, acordes sustentados',
            'bpm_range': (60, 70),
            'key_preferences': ['A', 'E', 'D', 'G'],
            'mode': 'major',
            'measures': 24,
            'has_drums': False,
            'drum_intensity': 'minimal',
        },
        LofiStyle.AMBIENT: {
            'name': 'Ambient Lo-Fi',
            'description': 'Atmosférico, foco em texturas e pads',
            'bpm_range': (60, 70),
            'key_preferences': ['A', 'E', 'D'],
            'mode': 'minor',
            'measures': 24,
            'has_drums': False,
            'drum_intensity': 'minimal',
        },
        LofiStyle.SAD: {
            'name': 'Sad Lo-Fi',
            'description': 'Progressões em tons menores, melodias melancólicas',
            'bpm_range': (70, 80),
            'key_preferences': ['Am', 'Dm', 'Em', 'Bm'],
            'mode': 'minor',
            'measures': 16,
            'has_drums': True,
            'drum_intensity': 'low',
        },
        LofiStyle.NOSTALGIC: {
            'name': 'Nostalgic Lo-Fi',
            'description': 'Melodias espaçadas e emotivas, progressões nostálgicas',
            'bpm_range': (70, 80),
            'key_preferences': ['C', 'G', 'D', 'A'],
            'mode': 'major',
            'measures': 16,
            'has_drums': True,
            'drum_intensity': 'low',
        },
    }
    
    def __init__(self, output_dir: str = './output'):
        """
        Inicializa o motor de geração
        
        Args:
            output_dir: Diretório para salvar arquivos MIDI gerados
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def _parse_key_and_mode(self, key_str: str) -> tuple:
        """
        Separa tonalidade e modo
        
        Args:
            key_str: String como 'C', 'Am', 'Dm', etc.
        
        Returns:
            Tupla (key, mode)
        """
        if key_str.endswith('m'):
            return key_str[:-1], 'minor'
        return key_str, 'major'
    
    def generate_track(self, 
                      style: LofiStyle,
                      key: Optional[str] = None,
                      bpm: Optional[int] = None,
                      measures: Optional[int] = None,
                      include_drums: Optional[bool] = None,
                      filename: Optional[str] = None) -> str:
        """
        Gera uma faixa Lo-Fi completa
        
        Args:
            style: Estilo de Lo-Fi (LofiStyle enum)
            key: Tonalidade (opcional, será escolhida automaticamente se None)
            bpm: BPM (opcional, será escolhido automaticamente se None)
            measures: Número de compassos (opcional)
            include_drums: Se deve incluir bateria (opcional)
            filename: Nome do arquivo (opcional)
        
        Returns:
            Caminho do arquivo MIDI gerado
        """
        # Carrega preset do estilo
        preset = self.STYLE_PRESETS[style]
        
        # Define parâmetros
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
        
        # Gera nome do arquivo
        if filename is None:
            filename = f"lofi_{preset['name'].lower().replace('/', '_').replace(' ', '_')}_{key}{mode[0]}_{bpm}bpm.mid"
        
        output_path = os.path.join(self.output_dir, filename)
        
        # Cria arquivo MIDI
        mid = MidiFile(ticks_per_beat=480)
        
        # Track de tempo (necessária para definir BPM)
        tempo_track = MidiTrack()
        mid.tracks.append(tempo_track)
        tempo_track.append(MetaMessage('track_name', name='Tempo', time=0))
        tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(bpm), time=0))
        tempo_track.append(MetaMessage('time_signature', numerator=4, denominator=4, 
                                       clocks_per_click=24, notated_32nd_notes_per_beat=8, time=0))
        
        # Gera harmonia e melodia
        print(f"Gerando {preset['name']} - Key: {key} {mode}, BPM: {bpm}, Measures: {measures}")
        
        generator = LofiMidiGenerator(style=style, key=key, mode=mode)
        generator.bpm = bpm  # Sobrescreve BPM
        
        # Track de harmonia
        harmony_track = MidiTrack()
        mid.tracks.append(harmony_track)
        harmony_track.append(MetaMessage('track_name', name='Harmony', time=0))
        harmony_track.append(Message('program_change', program=0, time=0, channel=0))  # Piano
        
        generator.generate_harmony_track(mid, harmony_track, measures=measures)
        
        # Track de melodia
        melody_track = MidiTrack()
        mid.tracks.append(melody_track)
        melody_track.append(MetaMessage('track_name', name='Melody', time=0))
        melody_track.append(Message('program_change', program=1, time=0, channel=1))  # Piano brilhante
        
        generator.generate_melody_track(mid, melody_track, measures=measures)
        
        # Adiciona bateria se necessário
        if include_drums:
            drum_gen = DrumGenerator(style=style, bpm=bpm)
            drum_track = drum_gen.generate_drum_track(mid, measures=measures)
            mid.tracks.append(drum_track)
            print(f"  ✓ Bateria adicionada com sincronia de grade")
        
        # Salva arquivo
        mid.save(output_path)
        print(f"  ✓ Arquivo salvo: {output_path}")
        
        return output_path
    
    def generate_all_styles(self, measures: int = 8) -> List[str]:
        """
        Gera exemplos de todos os estilos disponíveis
        
        Args:
            measures: Número de compassos para cada faixa
        
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        generated_files = []
        
        print("=" * 60)
        print("GERADOR DE MÚSICAS LO-FI - GERANDO TODOS OS ESTILOS")
        print("=" * 60)
        
        for style in LofiStyle:
            print(f"\n[{style.value.upper()}]")
            try:
                filepath = self.generate_track(style=style, measures=measures)
                generated_files.append(filepath)
            except Exception as e:
                print(f"  ✗ Erro ao gerar {style.value}: {e}")
        
        print("\n" + "=" * 60)
        print(f"GERAÇÃO CONCLUÍDA: {len(generated_files)} arquivos gerados")
        print("=" * 60)
        
        return generated_files
    
    def generate_variations(self, style: LofiStyle, count: int = 3, measures: int = 8) -> List[str]:
        """
        Gera múltiplas variações de um estilo
        
        Args:
            style: Estilo de Lo-Fi
            count: Número de variações
            measures: Número de compassos
        
        Returns:
            Lista de caminhos dos arquivos gerados
        """
        generated_files = []
        
        print(f"\nGerando {count} variações de {style.value}...")
        
        for i in range(count):
            filename = f"lofi_{style.value}_variation_{i+1}.mid"
            filepath = self.generate_track(style=style, measures=measures, filename=filename)
            generated_files.append(filepath)
        
        return generated_files
    
    @staticmethod
    def list_styles() -> Dict[str, str]:
        """
        Lista todos os estilos disponíveis com descrições
        
        Returns:
            Dicionário {estilo: descrição}
        """
        styles = {}
        for style, preset in LofiEngine.STYLE_PRESETS.items():
            styles[preset['name']] = preset['description']
        return styles


# Importa Message para uso no código
from mido import Message


def main():
    """Função principal para demonstração e testes"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gerador de Músicas Lo-Fi em MIDI')
    parser.add_argument('--style', type=str, choices=[s.value for s in LofiStyle],
                       help='Estilo de Lo-Fi a gerar')
    parser.add_argument('--key', type=str, help='Tonalidade (ex: C, Am, F#, Bbm)')
    parser.add_argument('--bpm', type=int, help='BPM (batidas por minuto)')
    parser.add_argument('--measures', type=int, default=16, help='Número de compassos')
    parser.add_argument('--no-drums', action='store_true', help='Gerar sem bateria')
    parser.add_argument('--output', type=str, default='./output', help='Diretório de saída')
    parser.add_argument('--all', action='store_true', help='Gerar todos os estilos')
    parser.add_argument('--variations', type=int, help='Número de variações a gerar')
    parser.add_argument('--list', action='store_true', help='Listar estilos disponíveis')
    
    args = parser.parse_args()
    
    # Lista estilos
    if args.list:
        print("\nEstilos de Lo-Fi disponíveis:\n")
        for name, desc in LofiEngine.list_styles().items():
            print(f"  • {name}: {desc}")
        return
    
    # Cria engine
    engine = LofiEngine(output_dir=args.output)
    
    # Gera todos os estilos
    if args.all:
        engine.generate_all_styles(measures=args.measures)
        return
    
    # Gera variações
    if args.variations and args.style:
        style = LofiStyle(args.style)
        engine.generate_variations(style=style, count=args.variations, measures=args.measures)
        return
    
    # Gera faixa única
    if args.style:
        style = LofiStyle(args.style)
        engine.generate_track(
            style=style,
            key=args.key,
            bpm=args.bpm,
            measures=args.measures,
            include_drums=not args.no_drums
        )
    else:
        print("Use --style para especificar um estilo, --all para gerar todos, ou --list para listar estilos.")
        print("Exemplo: python lofi_engine.py --style chillhop --key C --bpm 85 --measures 16")


if __name__ == "__main__":
    main()
