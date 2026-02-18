"""
Gerador de Bateria Lo-Fi em formato MIDI - Versão Sincronizada
Garante que a bateria esteja perfeitamente alinhada à grade de ticks.
"""

import random
from mido import MidiTrack, Message
from typing import List, Tuple

class DrumGenerator:
    KICK = 36
    SNARE = 38
    RIMSHOT = 37
    CLOSED_HH = 42

    def __init__(self, style, bpm):
        self.style = style
        self.bpm = bpm

    def generate_drum_track(self, mid, measures: int = 8) -> MidiTrack:
        track = MidiTrack()
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            m_offset = m * ticks_per_measure
            
            # Kick nos tempos 1 e 3 (grade cravada)
            for b in [0, 2]:
                t = m_offset + b * ticks_per_beat
                events.append((t, 'on', self.KICK, 80))
                events.append((t + 100, 'off', self.KICK, 0))
            
            # Snare nos tempos 2 e 4 (grade cravada)
            for b in [1, 3]:
                t = m_offset + b * ticks_per_beat
                events.append((t, 'on', self.SNARE, 70))
                events.append((t + 100, 'off', self.SNARE, 0))
            
            # Hi-hat em colcheias (swing de tercina)
            swing = 0.6 # 60% swing
            for b in range(4):
                # Cabeça do tempo
                t1 = m_offset + b * ticks_per_beat
                events.append((t1, 'on', self.CLOSED_HH, 60))
                events.append((t1 + 80, 'off', self.CLOSED_HH, 0))
                
                # Contratempo com swing
                t2 = m_offset + b * ticks_per_beat + int(ticks_per_beat * swing)
                events.append((t2, 'on', self.CLOSED_HH, 45))
                events.append((t2 + 80, 'off', self.CLOSED_HH, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', 
                                 note=note, velocity=vel, time=delta, channel=9))
            last_tick = tick
        return track
