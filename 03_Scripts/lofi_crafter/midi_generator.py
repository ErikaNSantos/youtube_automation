"""
Gerador de Músicas Lo-Fi em formato MIDI - Versão Sincronizada (Fix Assinatura)
Garante que harmonia e melodia estejam perfeitamente alinhadas ao tempo da bateria.
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
    MAJOR7 = [0, 4, 7, 11]
    MINOR7 = [0, 3, 7, 10]
    DOMINANT7 = [0, 4, 7, 10]
    MINOR7B5 = [0, 3, 6, 10]
    MAJOR9 = [0, 4, 7, 11, 14]
    MINOR9 = [0, 3, 7, 10, 14]


class LofiMidiGenerator:
    """Gerador MIDI com sincronia absoluta de ticks para evitar desencontro rítmico"""
    
    SCALES = {
        'major': [0, 2, 4, 5, 7, 9, 11],
        'minor': [0, 2, 3, 5, 7, 8, 10],
    }

    PROGRESSIONS = {
        'major': [[(1, ChordQuality.MAJOR7), (6, ChordQuality.MINOR7), (2, ChordQuality.MINOR7), (5, ChordQuality.DOMINANT7)]],
        'minor': [[(1, ChordQuality.MINOR7), (4, ChordQuality.MINOR7), (7, ChordQuality.DOMINANT7), (3, ChordQuality.MAJOR7)]]
    }

    def __init__(self, style: LofiStyle = LofiStyle.CHILLHOP, key: str = 'C', mode: str = 'major'):
        self.style = style
        self.key_root = self._parse_key(key)
        self.mode = mode if mode in self.SCALES else 'major'
        self.scale = self.SCALES[self.mode]
        self.bpm = random.randint(75, 85)

    def _parse_key(self, key: str) -> int:
        key_map = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
        return key_map.get(key.upper(), 0)

    def _get_note(self, degree: int, octave: int) -> int:
        idx = (degree - 1) % 7
        return self.key_root + self.scale[idx] + (octave + (degree - 1) // 7) * 12

    def _humanize_time(self) -> int:
        return random.randint(-15, 15)

    def generate_harmony_track(self, mid: MidiFile, track: MidiTrack, measures: int = 8, chords_per_measure: int = 1):
        # Limpa o track para evitar lixo de chamadas anteriores se necessário, 
        # mas aqui o lofi_engine passa o track já criado
        track.append(Message('program_change', program=0, time=0))
        ticks_per_measure = mid.ticks_per_beat * 4
        prog = random.choice(self.PROGRESSIONS['minor' if self.mode == 'minor' else 'major'])
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            root = self._get_note(degree, 3)
            chord = [root + i for i in quality.value]
            
            start_tick = m * ticks_per_measure
            duration = ticks_per_measure - 40
            
            for note in chord:
                h_time = start_tick + self._humanize_time()
                events.append((max(0, h_time), 'on', note))
                events.append((start_tick + duration, 'off', note))

        events.sort()
        last_tick = 0
        for tick, type, note in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', 
                                 note=note, velocity=60 if type == 'on' else 0, time=delta))
            last_tick = tick

    def generate_melody_track(self, mid: MidiFile, track: MidiTrack, measures: int = 8):
        track.append(Message('program_change', program=1, time=0))
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        prog = random.choice(self.PROGRESSIONS['minor' if self.mode == 'minor' else 'major'])
        
        events = []
        for m in range(measures):
            degree, quality = prog[m % len(prog)]
            chord_notes = [self._get_note(degree, 4) + i for i in quality.value]
            
            for b in range(4):
                start_tick = m * ticks_per_measure + b * ticks_per_beat
                if random.random() < 0.8:
                    note = random.choice(chord_notes) + 12
                    h_on = start_tick + self._humanize_time()
                    h_off = start_tick + ticks_per_beat - 40
                    events.append((max(0, h_on), 'on', note))
                    events.append((h_off, 'off', note))

        events.sort()
        last_tick = 0
        for tick, type, note in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', 
                                 note=note, velocity=80 if type == 'on' else 0, time=delta))
            last_tick = tick

    def generate(self, output_path: str, measures: int = 8):
        mid = MidiFile(ticks_per_beat=480)
        
        meta = MidiTrack()
        mid.tracks.append(meta)
        meta.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(self.bpm)))
        
        harmony_track = MidiTrack()
        mid.tracks.append(harmony_track)
        self.generate_harmony_track(mid, harmony_track, measures)
        
        melody_track = MidiTrack()
        mid.tracks.append(melody_track)
        self.generate_melody_track(mid, melody_track, measures)
        
        mid.save(output_path)
        return output_path
