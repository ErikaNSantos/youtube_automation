"""
Gerador de Músicas Lo-Fi - Versão Expandida Multi-Instrumental
Implementa tracks de Piano, Bass, Pad, Violino, Guitarra Jazz e Flauta.
Foco em harmonia de 7ª/9ª e composição melancólica e espaçada.
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
    """Gerador MIDI multi-instrumental com foco em melancolia e humanização."""
    
    SCALES = {
        'minor': [0, 2, 3, 5, 7, 8, 10],
        'dorian': [0, 2, 3, 5, 7, 9, 10],
    }

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
        self.bpm = random.randint(70, 80)
        self.swing = 0.58

    def _parse_key(self, key: str) -> int:
        key_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        return key_map.get(key.upper(), 9)

    def _get_note(self, degree: int, octave: int) -> int:
        idx = (degree - 1) % 7
        return self.key_root + self.scale[idx] + (octave + (degree - 1) // 7) * 12

    def _humanize_velocity(self, base_vel: int, variance: int = 20) -> int:
        return max(30, min(110, base_vel + random.randint(-variance, variance)))

    def _humanize_time(self, variance: int = 30) -> int:
        return random.randint(-variance, variance)

    def generate_harmony_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Piano de Feltro (Harmonia)"""
        track = MidiTrack()
        track.append(Message('program_change', program=0, time=0, channel=0))
        ticks_per_measure = mid.ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            root = self._get_note(degree, 3)
            chord = [root + i for i in quality.value]
            start_tick = m * ticks_per_measure
            for note in chord:
                h_on = start_tick + self._humanize_time(40)
                h_off = start_tick + ticks_per_measure - 60
                events.append((max(0, h_on), 'on', note, self._humanize_velocity(45, 10)))
                events.append((h_off, 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=0))
            last_tick = tick
        return track

    def generate_bass_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Contra-baixo (Bass)"""
        track = MidiTrack()
        track.append(Message('program_change', program=32, time=0, channel=1))
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, _ = prog[m % len(prog)]
            root = self._get_note(degree, 2)
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
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=1))
            last_tick = tick
        return track

    def generate_pad_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Pads Atmosféricos"""
        track = MidiTrack()
        track.append(Message('program_change', program=89, time=0, channel=2))
        ticks_per_measure = mid.ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            root = self._get_note(degree, 4)
            chord = [root, root + quality.value[1], root + quality.value[2]]
            start_tick = m * ticks_per_measure
            for note in chord:
                events.append((start_tick, 'on', note, 35))
                events.append((start_tick + ticks_per_measure, 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=2))
            last_tick = tick
        return track

    def generate_strings_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Violino/Strings (Melodia Melancólica Longa)"""
        track = MidiTrack()
        track.append(Message('program_change', program=40, time=0, channel=3)) # Violin
        ticks_per_measure = mid.ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            if random.random() < 0.4: # Toca apenas ocasionalmente para não poluir
                degree, quality = prog[m % len(prog)]
                note = self._get_note(degree, 5) + random.choice([0, 3, 7]) # Nota da tríade
                start_tick = m * ticks_per_measure + int(mid.ticks_per_beat * 0.5)
                duration = ticks_per_measure - int(mid.ticks_per_beat * 1.0)
                
                events.append((start_tick, 'on', note, 45))
                events.append((start_tick + duration, 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=3))
            last_tick = tick
        return track

    def generate_guitar_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Guitarra Jazz (Muted/Clean)"""
        track = MidiTrack()
        track.append(Message('program_change', program=26, time=0, channel=4)) # Electric Guitar (Jazz)
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            if random.random() < 0.5:
                degree, quality = prog[m % len(prog)]
                chord_notes = [self._get_note(degree, 4) + i for i in quality.value]
                
                # Arpejo curto ou nota isolada
                for b in [1.5, 3.5]:
                    if random.random() < 0.6:
                        note = random.choice(chord_notes)
                        start_tick = int(m * ticks_per_measure + b * ticks_per_beat)
                        events.append((start_tick, 'on', note, 55))
                        events.append((start_tick + int(ticks_per_beat * 0.5), 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=4))
            last_tick = tick
        return track

    def generate_flute_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Flauta (Melodia Espaçada e Etérea)"""
        track = MidiTrack()
        track.append(Message('program_change', program=73, time=0, channel=5)) # Flute
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(0, measures, 2): # Melodia de flauta a cada 2 compassos
            if random.random() < 0.5:
                degree, _ = prog[m % len(prog)]
                notes = [self._get_note(degree, 6), self._get_note(degree, 6) + 2, self._get_note(degree, 6) - 2]
                
                start_tick = m * ticks_per_measure + int(ticks_per_beat * 2)
                for i, note in enumerate(notes[:2]):
                    t = start_tick + i * int(ticks_per_beat * 1.0)
                    events.append((t, 'on', note, 40))
                    events.append((t + int(ticks_per_beat * 0.8), 'off', note, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=5))
            last_tick = tick
        return track

    def generate_melody_track(self, mid: MidiFile, prog: List, measures: int) -> MidiTrack:
        """Track: Melodia Principal (Piano)"""
        track = MidiTrack()
        track.append(Message('program_change', program=1, time=0, channel=6))
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            chord_notes = [self._get_note(degree, 4) + i for i in quality.value]
            for b in [0.5, 2, 3.5]:
                if random.random() < 0.6:
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
            track.append(Message('note_on' if type == 'on' else 'note_off', note=note, velocity=vel, time=delta, channel=6))
            last_tick = tick
        return track

    def generate_full_ensemble(self, mid: MidiFile, prog: List, measures: int, instruments: List[str] = None):
        """
        Gera um arranjo completo com base na lista de instrumentos desejada.
        """
        if instruments is None:
            instruments = ['piano', 'bass', 'pad', 'melody'] # Core padrão
            
        # Adiciona tracks baseadas na lista de instrumentos
        if 'piano' in instruments:
            mid.tracks.append(self.generate_harmony_track(mid, prog, measures))
        if 'bass' in instruments:
            mid.tracks.append(self.generate_bass_track(mid, prog, measures))
        if 'pad' in instruments:
            mid.tracks.append(self.generate_pad_track(mid, prog, measures))
        if 'strings' in instruments or 'violin' in instruments:
            mid.tracks.append(self.generate_strings_track(mid, prog, measures))
        if 'guitar' in instruments:
            mid.tracks.append(self.generate_guitar_track(mid, prog, measures))
        if 'flute' in instruments:
            mid.tracks.append(self.generate_flute_track(mid, prog, measures))
        if 'melody' in instruments:
            mid.tracks.append(self.generate_melody_track(mid, prog, measures))

    def generate(self, output_path: str, measures: int = 16, instruments: List[str] = None):
        mid = MidiFile(ticks_per_beat=480)
        prog = random.choice(self.MELANCHOLIC_PROGRESSIONS)
        
        # Track 0: Meta
        meta = MidiTrack()
        mid.tracks.append(meta)
        meta.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm)))
        meta.append(MetaMessage('track_name', name='LoFi Master Clock'))

        # Gerar Ensemble
        self.generate_full_ensemble(mid, prog, measures, instruments)
        
        mid.save(output_path)
        return output_path
