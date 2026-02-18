"""
Gerador de Músicas Lo-Fi em formato MIDI - Versão Corrigida (Afinação)
Implementa geração de harmonia, melodia e humanização com foco em coerência tonal.
"""

import random
import mido
from mido import MidiFile, MidiTrack, Message, MetaMessage
from typing import List, Tuple, Dict, Optional
from enum import Enum


class LofiStyle(Enum):
    CHILLHOP = "chillhop"
    JAZZHOP = "jazzhop"
    SLEEP = "sleep"
    AMBIENT = "ambient"
    SAD = "sad"
    NOSTALGIC = "nostalgic"


class ChordQuality(Enum):
    # Intervalos em semitons
    MAJOR7 = [0, 4, 7, 11]
    MINOR7 = [0, 3, 7, 10]
    DOMINANT7 = [0, 4, 7, 10]
    MINOR7B5 = [0, 3, 6, 10]
    MAJOR9 = [0, 4, 7, 11, 14]
    MINOR9 = [0, 3, 7, 10, 14]
    DOMINANT9 = [0, 4, 7, 10, 14]


class LofiMidiGenerator:
    """Gerador MIDI com lógica harmônica aprimorada para evitar desafinação"""
    
    # Mapeamento de escalas diatônicas (intervalos relativos à tônica)
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
    }

    # Graus da escala para cada modo (1-based)
    # ii-V-I em Maior: 2m7, 57, 1maj7
    # ii-V-i em Menor: 2m7b5, 57, 1m7
    PROGRESSIONS = {
        'major': [
            [(2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7), (1, ChordQuality.MAJOR7), (1, ChordQuality.MAJOR7)],
            [(1, ChordQuality.MAJOR7), (6, ChordQuality.MINOR7), (2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7)],
            [(4, ChordQuality.MAJOR7), (5, ChordQuality.DOMINANT7), (3, ChordQuality.MINOR7), (6, ChordQuality.MINOR7)],
        ],
        'minor': [
            [(1, ChordQuality.MINOR7), (4, ChordQuality.MINOR7), (7, ChordQuality.DOMINANT7), (3, ChordQuality.MAJOR7)],
            [(1, ChordQuality.MINOR7), (6, ChordQuality.MAJOR7), (2, ChordQuality.MINOR7B5), (5, ChordQuality.DOMINANT7)],
            [(6, ChordQuality.MAJOR7), (5, ChordQuality.DOMINANT7), (1, ChordQuality.MINOR7), (1, ChordQuality.MINOR7)],
        ]
    }

    def __init__(self, style: LofiStyle = LofiStyle.CHILLHOP, key: str = 'C', mode: str = 'major'):
        self.style = style
        self.key_str = key
        self.mode = mode if mode in self.SCALES else 'major'
        self.key_root = self._parse_key(key)
        self.scale_intervals = self.SCALES[self.mode]
        self.bpm = self._get_bpm_for_style()

    def _parse_key(self, key: str) -> int:
        key_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        return key_map.get(key.upper(), 0)

    def _get_bpm_for_style(self) -> int:
        if self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]: return random.randint(60, 70)
        return random.randint(75, 90)

    def _get_note_from_scale(self, degree: int, octave: int) -> int:
        """Retorna a nota MIDI exata para um grau da escala (1-7)"""
        idx = (degree - 1) % 7
        octave_add = (degree - 1) // 7
        return self.key_root + self.scale_intervals[idx] + (octave + octave_add) * 12

    def _get_chord_progression(self) -> List[Tuple[int, ChordQuality]]:
        """Seleciona uma progressão coerente com o modo"""
        mode_category = 'minor' if self.mode in ['minor', 'dorian'] else 'major'
        return random.choice(self.PROGRESSIONS[mode_category])

    def _humanize(self, value: int, variance: float) -> int:
        return int(value * (1 + random.uniform(-variance, variance)))

    def generate_harmony_track(self, mid: MidiFile, track: MidiTrack, measures: int = 8):
        ticks_per_measure = mid.ticks_per_beat * 4
        progression = self._get_chord_progression()
        
        for m in range(measures):
            degree, quality = progression[m % len(progression)]
            root_note = self._get_note_from_scale(degree, 3)
            chord_notes = [root_note + i for i in quality.value]
            
            # Note ON
            for i, note in enumerate(chord_notes):
                vel = self._humanize(60, 0.1)
                time = self._humanize(5, 0.5) if i == 0 else 0
                track.append(Message('note_on', note=note, velocity=vel, time=time))
            
            # Note OFF (Dura o compasso quase todo)
            off_time = ticks_per_measure - 20
            for i, note in enumerate(chord_notes):
                track.append(Message('note_off', note=note, velocity=0, time=off_time if i == 0 else 0))

    def generate_melody_track(self, mid: MidiFile, track: MidiTrack, measures: int = 8):
        ticks_per_beat = mid.ticks_per_beat
        progression = self._get_chord_progression()
        
        for m in range(measures):
            degree, quality = progression[m % len(progression)]
            chord_root = self._get_note_from_scale(degree, 4)
            chord_notes = [chord_root + i for i in quality.value]
            
            # Melodia: 4 notas por compasso (semínimas)
            for _ in range(4):
                # Escolhe nota: 70% chance nota do acorde, 30% nota da escala
                if random.random() < 0.7:
                    note = random.choice(chord_notes) + 12 # Oitava acima
                else:
                    scale_degree = random.randint(1, 7)
                    note = self._get_note_from_scale(scale_degree, 5)
                
                # Humanização
                vel = self._humanize(80, 0.15)
                start_delay = self._humanize(10, 0.2)
                duration = self._humanize(ticks_per_beat - 40, 0.1)
                
                track.append(Message('note_on', note=note, velocity=vel, time=start_delay))
                track.append(Message('note_off', note=note, velocity=0, time=duration))

    def generate(self, output_path: str, measures: int = 8):
        mid = MidiFile(ticks_per_beat=480)
        
        # Track 0: Meta
        meta = MidiTrack()
        mid.tracks.append(meta)
        meta.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm)))
        meta.append(MetaMessage('track_name', name='Control'))

        # Track 1: Harmony
        harmony = MidiTrack()
        mid.tracks.append(harmony)
        harmony.append(Message('program_change', program=0, time=0)) # Piano
        self.generate_harmony_track(mid, harmony, measures)

        # Track 2: Melody
        melody = MidiTrack()
        mid.tracks.append(melody)
        melody.append(Message('program_change', program=1, time=0)) # Bright Piano
        self.generate_melody_track(mid, melody, measures)

        mid.save(output_path)
        return output_path
