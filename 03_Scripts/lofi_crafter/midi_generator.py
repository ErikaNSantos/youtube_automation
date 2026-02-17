"""
Gerador de Músicas Lo-Fi em formato MIDI
Implementa geração de harmonia, melodia e humanização
"""

import random
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
from typing import List, Tuple, Dict, Optional
from enum import Enum


class LofiStyle(Enum):
    """Estilos de Lo-Fi disponíveis"""
    CHILLHOP = "chillhop"
    JAZZHOP = "jazzhop"
    SLEEP = "sleep"
    AMBIENT = "ambient"
    SAD = "sad"
    NOSTALGIC = "nostalgic"


class ChordQuality(Enum):
    """Qualidades de acordes para Lo-Fi/Jazz"""
    MAJOR7 = [0, 4, 7, 11]
    MINOR7 = [0, 3, 7, 10]
    DOMINANT7 = [0, 4, 7, 10]
    MINOR7B5 = [0, 3, 6, 10]  # Half-diminished
    MAJOR9 = [0, 4, 7, 11, 14]
    MINOR9 = [0, 3, 7, 10, 14]
    DOMINANT9 = [0, 4, 7, 10, 14]
    MAJOR6 = [0, 4, 7, 9]
    MINOR6 = [0, 3, 7, 9]


class LofiMidiGenerator:
    """Gerador principal de arquivos MIDI Lo-Fi"""
    
    # Notas MIDI (C4 = 60)
    C4 = 60
    
    # Progressões harmônicas típicas (em graus da escala)
    CHORD_PROGRESSIONS = {
        'ii_V_I': [(2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7), (1, ChordQuality.MAJOR7)],
        'I_vi_ii_V': [(1, ChordQuality.MAJOR7), (6, ChordQuality.MINOR7), (2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7)],
        'vi_ii_V_I': [(6, ChordQuality.MINOR7), (2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7), (1, ChordQuality.MAJOR7)],
        'I_IV_vi_V': [(1, ChordQuality.MAJOR7), (4, ChordQuality.MAJOR7), (6, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7)],
        'ii_V_I_vi': [(2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7), (1, ChordQuality.MAJOR7), (6, ChordQuality.MINOR7)],
        'sad_progression': [(6, ChordQuality.MINOR7), (4, ChordQuality.MAJOR7), (1, ChordQuality.MAJOR7), (5, ChordQuality.DOMINANT7)],
        'nostalgic': [(1, ChordQuality.MAJOR7), (3, ChordQuality.MINOR7), (6, ChordQuality.MINOR7), (2, ChordQuality.MINOR7)],
    }
    
    # Escalas (intervalos em semitons a partir da tônica)
    MAJOR_SCALE = [0, 2, 4, 5, 7, 9, 11]
    MINOR_SCALE = [0, 2, 3, 5, 7, 8, 10]
    DORIAN_SCALE = [0, 2, 3, 5, 7, 9, 10]
    
    def __init__(self, style: LofiStyle = LofiStyle.CHILLHOP, key: str = 'C', mode: str = 'major'):
        """
        Inicializa o gerador
        
        Args:
            style: Estilo de Lo-Fi a ser gerado
            key: Tonalidade (C, D, E, F, G, A, B com # ou b)
            mode: Modo (major, minor, dorian)
        """
        self.style = style
        self.key = key
        self.mode = mode
        self.bpm = self._get_bpm_for_style()
        self.key_note = self._parse_key(key)
        self.scale = self._get_scale()
        
    def _get_bpm_for_style(self) -> int:
        """Retorna BPM apropriado para o estilo"""
        if self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]:
            return random.randint(60, 70)
        elif self.style in [LofiStyle.SAD, LofiStyle.NOSTALGIC]:
            return random.randint(70, 80)
        else:  # CHILLHOP, JAZZHOP
            return random.randint(75, 90)
    
    def _parse_key(self, key: str) -> int:
        """Converte string de tonalidade para número MIDI"""
        key_map = {
            'C': 0, 'C#': 1, 'Db': 1,
            'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
            'G': 7, 'G#': 8, 'Ab': 8,
            'A': 9, 'A#': 10, 'Bb': 10,
            'B': 11
        }
        return key_map.get(key, 0)
    
    def _get_scale(self) -> List[int]:
        """Retorna a escala apropriada para o modo"""
        if self.mode == 'minor':
            return self.MINOR_SCALE
        elif self.mode == 'dorian':
            return self.DORIAN_SCALE
        else:
            return self.MAJOR_SCALE
    
    def _get_chord_progression(self) -> List[Tuple[int, ChordQuality]]:
        """Seleciona progressão de acordes baseada no estilo"""
        if self.style == LofiStyle.SAD:
            return self.CHORD_PROGRESSIONS['sad_progression']
        elif self.style == LofiStyle.NOSTALGIC:
            return self.CHORD_PROGRESSIONS['nostalgic']
        elif self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]:
            return self.CHORD_PROGRESSIONS['I_IV_vi_V']
        else:
            # Escolhe aleatoriamente entre progressões jazzísticas
            progressions = ['ii_V_I', 'I_vi_ii_V', 'vi_ii_V_I', 'ii_V_I_vi']
            return self.CHORD_PROGRESSIONS[random.choice(progressions)]
    
    def _degree_to_note(self, degree: int, octave: int = 4) -> int:
        """Converte grau da escala para nota MIDI"""
        scale_index = (degree - 1) % 7
        octave_offset = (degree - 1) // 7
        note = self.key_note + self.scale[scale_index] + (octave + octave_offset) * 12
        return note
    
    def _build_chord(self, degree: int, quality: ChordQuality, octave: int = 3) -> List[int]:
        """Constrói um acorde a partir do grau e qualidade"""
        root = self._degree_to_note(degree, octave)
        return [root + interval for interval in quality.value]
    
    def _humanize_timing(self, base_time: int, amount: float = 0.05) -> int:
        """
        Aplica humanização ao timing
        
        Args:
            base_time: Tempo base em ticks
            amount: Quantidade de humanização (0.0 a 1.0)
        
        Returns:
            Tempo humanizado em ticks
        """
        variation = int(base_time * amount * random.uniform(-1, 1))
        return max(0, base_time + variation)
    
    def _humanize_velocity(self, base_velocity: int, amount: float = 0.15) -> int:
        """
        Aplica humanização à velocidade (volume)
        
        Args:
            base_velocity: Velocidade base (0-127)
            amount: Quantidade de humanização (0.0 a 1.0)
        
        Returns:
            Velocidade humanizada (0-127)
        """
        variation = int(base_velocity * amount * random.uniform(-1, 1))
        return max(20, min(127, base_velocity + variation))
    
    def _generate_melody_notes(self, chord_notes: List[int], num_notes: int = 8) -> List[Tuple[int, int]]:
        """
        Gera notas melódicas baseadas no acorde
        
        Args:
            chord_notes: Notas do acorde atual
            num_notes: Número de notas a gerar
        
        Returns:
            Lista de tuplas (nota, duração_relativa)
        """
        melody = []
        
        # Notas disponíveis: notas do acorde + notas da escala próximas
        available_notes = chord_notes.copy()
        for note in chord_notes:
            # Adiciona notas da escala uma oitava acima
            for interval in self.scale:
                scale_note = note + interval
                if scale_note not in available_notes:
                    available_notes.append(scale_note)
        
        available_notes.sort()
        
        # Gera melodia
        current_note = random.choice(chord_notes)
        
        for i in range(num_notes):
            # Decide se toca nota ou pausa
            if random.random() < 0.2:  # 20% chance de pausa
                melody.append((0, 1))  # 0 = pausa
            else:
                # Movimento melódico (preferência por graus conjuntos)
                if random.random() < 0.7:  # 70% movimento por grau conjunto
                    # Encontra notas próximas
                    nearby = [n for n in available_notes if abs(n - current_note) <= 3]
                    if nearby:
                        current_note = random.choice(nearby)
                else:
                    # Salto melódico
                    current_note = random.choice(available_notes)
                
                # Duração variada
                duration = random.choice([1, 2, 3, 4])
                melody.append((current_note + 12, duration))  # +12 para oitava acima
        
        return melody
    
    def generate_harmony_track(self, mid: MidiFile, track: MidiTrack, 
                               measures: int = 8, chords_per_measure: int = 1):
        """
        Gera track de harmonia (acordes)
        
        Args:
            mid: Arquivo MIDI
            track: Track MIDI
            measures: Número de compassos
            chords_per_measure: Acordes por compasso
        """
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4  # Compasso 4/4
        chord_duration = ticks_per_measure // chords_per_measure
        
        progression = self._get_chord_progression()
        
        # Velocidade base para acordes
        base_velocity = 60 if self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT] else 70
        
        time_offset = 0
        
        for measure in range(measures):
            chord_data = progression[measure % len(progression)]
            degree, quality = chord_data
            
            # Constrói o acorde
            chord_notes = self._build_chord(degree, quality, octave=3)
            
            # Toca as notas do acorde
            for note in chord_notes:
                velocity = self._humanize_velocity(base_velocity)
                timing_offset = self._humanize_timing(0, amount=0.02)
                
                track.append(Message('note_on', note=note, velocity=velocity, 
                                    time=timing_offset if note == chord_notes[0] else 0))
            
            # Aguarda duração do acorde
            time_offset = chord_duration - sum(msg.time for msg in track[-len(chord_notes):])
            
            # Desliga as notas
            for i, note in enumerate(chord_notes):
                track.append(Message('note_off', note=note, velocity=0, 
                                    time=time_offset if i == 0 else 0))
                time_offset = 0
    
    def generate_melody_track(self, mid: MidiFile, track: MidiTrack, 
                             measures: int = 8):
        """
        Gera track de melodia
        
        Args:
            mid: Arquivo MIDI
            track: Track MIDI
            measures: Número de compassos
        """
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        progression = self._get_chord_progression()
        
        # Velocidade base para melodia
        base_velocity = 75 if self.style in [LofiStyle.CHILLHOP, LofiStyle.JAZZHOP] else 65
        
        for measure in range(measures):
            chord_data = progression[measure % len(progression)]
            degree, quality = chord_data
            
            # Constrói o acorde para referência melódica
            chord_notes = self._build_chord(degree, quality, octave=4)
            
            # Gera notas melódicas
            melody_notes = self._generate_melody_notes(chord_notes, num_notes=8)
            
            note_duration = ticks_per_measure // 8
            
            for note, duration in melody_notes:
                if note == 0:  # Pausa
                    track.append(Message('note_on', note=60, velocity=0, time=note_duration))
                else:
                    velocity = self._humanize_velocity(base_velocity)
                    timing = self._humanize_timing(0, amount=0.03)
                    
                    # Note on
                    track.append(Message('note_on', note=note, velocity=velocity, time=timing))
                    
                    # Note off
                    note_off_time = self._humanize_timing(note_duration * duration, amount=0.02)
                    track.append(Message('note_off', note=note, velocity=0, time=note_off_time))
    
    def generate(self, output_path: str, measures: int = 8) -> str:
        """
        Gera arquivo MIDI completo
        
        Args:
            output_path: Caminho para salvar o arquivo .mid
            measures: Número de compassos
        
        Returns:
            Caminho do arquivo gerado
        """
        # Cria arquivo MIDI
        mid = MidiFile(ticks_per_beat=480)
        
        # Track de harmonia
        harmony_track = MidiTrack()
        mid.tracks.append(harmony_track)
        
        # Configurações iniciais
        harmony_track.append(MetaMessage('track_name', name='Harmony', time=0))
        harmony_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm), time=0))
        harmony_track.append(Message('program_change', program=0, time=0))  # Piano
        
        # Gera harmonia
        self.generate_harmony_track(mid, harmony_track, measures=measures)
        
        # Track de melodia
        melody_track = MidiTrack()
        mid.tracks.append(melody_track)
        
        melody_track.append(MetaMessage('track_name', name='Melody', time=0))
        melody_track.append(Message('program_change', program=1, time=0))  # Piano brilhante
        
        # Gera melodia
        self.generate_melody_track(mid, melody_track, measures=measures)
        
        # Salva arquivo
        mid.save(output_path)
        
        return output_path


if __name__ == "__main__":
    # Teste básico
    generator = LofiMidiGenerator(style=LofiStyle.CHILLHOP, key='C', mode='major')
    output = generator.generate('test_lofi.mid', measures=8)
    print(f"Arquivo MIDI gerado: {output}")
