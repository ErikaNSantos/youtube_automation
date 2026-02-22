"""
Gerador de Músicas Lo-Fi - Versão Melancólica e Humanizada (Alta Fidelidade)
Implementa 4 tracks (Piano, Bass, Pad, Drums) com harmonia de 7ª/9ª e humanização agressiva.
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
    MINOR7 = [0, 3, 7, 10]
    MINOR9 = [0, 3, 7, 10, 14]
    MAJOR7 = [0, 4, 7, 11]
    DOMINANT7 = [0, 4, 7, 10]
    MINOR7B5 = [0, 3, 6, 10]


class LofiMidiGenerator:
    """Gerador MIDI com foco em melancolia, texturas e humanização (swing/velocity)"""
    
    # Escalas menores e dóricas (foco melancólico)
    SCALES = {
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
    }

    # Progressões melancólicas e introspectivas
    MELANCHOLIC_PROGRESSIONS = [
        [(1, ChordQuality.MINOR9), (4, ChordQuality.MINOR7), (7, ChordQuality.DOMINANT7), (3, ChordQuality.MAJOR7)],
        [(1, ChordQuality.MINOR7), (6, ChordQuality.MAJOR7), (2, ChordQuality.MINOR7B5), (5, ChordQuality.DOMINANT7)],
        [(6, ChordQuality.MAJOR7), (5, ChordQuality.DOMINANT7), (1, ChordQuality.MINOR9), (1, ChordQuality.MINOR7)],
        [(1, ChordQuality.MINOR7), (4, ChordQuality.MINOR9), (1, ChordQuality.MINOR7), (4, ChordQuality.MINOR7)],
    ]

    def __init__(self, key: str = 'A', mode: str = 'minor'):
        self.key_root = self._parse_key(key)
        self.mode = mode if mode in self.SCALES else 'minor'
        self.scale = self.SCALES[self.mode]
        self.bpm = random.randint(70, 80) # Lo-Fi é mais lento
        self.swing = 0.58 # Swing sutil de tercina (58-62%)

    def _parse_key(self, key: str) -> int:
        key_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        return key_map.get(key.upper(), 9) # Default A minor

    def _get_note(self, degree: int, octave: int) -> int:
        idx = (degree - 1) % 7
        return self.key_root + self.scale[idx] + (octave + (degree - 1) // 7) * 12

    def _humanize_velocity(self, base_vel: int, variance: int = 25) -> int:
        """Variação agressiva de força para soar humano"""
        return max(30, min(110, base_vel + random.randint(-variance, variance)))

    def _humanize_time(self, variance: int = 30) -> int:
        """Micro-atrasos (lazy timing) característicos do Lo-Fi"""
        return random.randint(-variance, variance)

    def generate_harmony_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track 1: Piano de Feltro (Abafado)"""
        track = MidiTrack()
        track.append(Message('program_change', program=0, time=0)) # Piano
        ticks_per_measure = mid.ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            root = self._get_note(degree, 3)
            chord = [root + i for i in quality.value]
            
            start_tick = m * ticks_per_measure
            # Acordes longos e suaves
            for note in chord:
                h_on = start_tick + self._humanize_time(40)
                h_off = start_tick + ticks_per_measure - 60
                events.append((max(0, h_on), 'on', note, self._humanize_velocity(45, 10))) # Reduzido para dar espaço ao Bass/Kick
                events.append((h_off, 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta))
            last_tick = tick
        return track

    def generate_bass_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track 2: Contra-baixo (Grave e Marcado)"""
        track = MidiTrack()
        track.append(Message('program_change', program=32, time=0)) # Acoustic Bass
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, _ = prog[m % len(prog)]
            root = self._get_note(degree, 2) # Oitava bem baixa
            
            # Baixo toca no tempo 1 e ocasionalmente no 'e' do 2
            for b in [0, 1.5]:
                start_tick = int(m * ticks_per_measure + b * ticks_per_beat)
                h_on = start_tick + self._humanize_time(20)
                h_off = start_tick + int(ticks_per_beat * 0.8)
                events.append((max(0, h_on), 'on', root, self._humanize_velocity(70, 10)))
                events.append((h_off, 'off', root, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta))
            last_tick = tick
        return track

    def generate_pad_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track 3: Pads Atmosféricos (Sustentação)"""
        track = MidiTrack()
        track.append(Message('program_change', program=89, time=0)) # Pad (Warm)
        ticks_per_measure = mid.ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            root = self._get_note(degree, 4)
            # Apenas as notas fundamentais do acorde para ambiência
            chord = [root, root + quality.value[1], root + quality.value[2]]
            
            start_tick = m * ticks_per_measure
            for note in chord:
                events.append((start_tick, 'on', note, 40)) # Volume bem baixo
                events.append((start_tick + ticks_per_measure, 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta))
            last_tick = tick
        return track

    def generate_melody_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track 4: Melodia Melancólica (Espaçada)"""
        track = MidiTrack()
        track.append(Message('program_change', program=1, time=0)) # Piano Brilhante (ou Rhodes se SoundFont)
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            chord_notes = [self._get_note(degree, 4) + i for i in quality.value]
            
            # Melodia espaçada: toca apenas em alguns tempos para não poluir
            for b in [0.5, 2, 3.5]:
                if random.random() < 0.6: # 60% chance de nota
                    note = random.choice(chord_notes) + 12
                    start_tick = int(m * ticks_per_measure + b * ticks_per_beat)
                    h_on = start_tick + self._humanize_time(50)
                    h_off = start_tick + int(ticks_per_beat * 1.2)
                    events.append((max(0, h_on), 'on', note, self._humanize_velocity(75, 20)))
                    events.append((h_off, 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta))
            last_tick = tick
        return track

    def generate(self, output_path: str, measures: int = 16):
        mid = MidiFile(ticks_per_beat=480)
        prog = random.choice(self.MELANCHOLIC_PROGRESSIONS)
        
        # Track 0: Meta
        meta = MidiTrack()
        mid.tracks.append(meta)
        meta.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm)))
        meta.append(MetaMessage('track_name', name='LoFi Master Clock'))

        # Gerar Tracks
        mid.tracks.append(self.generate_harmony_track(mid, prog, measures))
        mid.tracks.append(self.generate_bass_track(mid, prog, measures))
        mid.tracks.append(self.generate_pad_track(mid, prog, measures))
        mid.tracks.append(self.generate_melody_track(mid, prog, measures))
        
        mid.save(output_path)
        return output_path
