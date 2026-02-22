"""
Gerador de Bateria Lo-Fi - Versão Humanizada e Orgânica
Implementa Swing, Ghost Notes e variações de Velocity para bateria acústica.
"""

import random
from mido import MidiTrack, Message
from typing import List, Tuple

class DrumGenerator:
    KICK = 36
    SNARE = 38
    RIMSHOT = 37
    CLOSED_HH = 42
    OPEN_HH = 46

    def __init__(self, style, bpm):
        self.style = style
        self.bpm = bpm
        # Swing agressivo de tercina (58-62% é o 'sweet spot' do Lo-Fi)
        self.swing = random.uniform(0.58, 0.62)

    def _humanize_velocity(self, base_vel: int, variance: int = 20) -> int:
        return max(20, min(120, base_vel + random.randint(-variance, variance)))

    def _humanize_time(self, variance: int = 15) -> int:
        """Micro-atrasos para o 'lazy groove'"""
        return random.randint(-variance, variance)

    def generate_drum_track(self, mid, measures: int = 16) -> MidiTrack:
        track = MidiTrack()
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4
        
        events = []
        for m in range(measures):
            m_offset = m * ticks_per_measure
            
            # 1. Kick (Bumbo) - Mais 'solto'
            for b in [0, 2.5]: # Kick no 1 e sincopado no 'e' do 3
                if b == 2.5 and random.random() < 0.4: continue # Ocasionalmente pula o sincopado
                t = int(m_offset + b * ticks_per_beat) + self._humanize_time(25)
                events.append((max(0, t), 'on', self.KICK, self._humanize_velocity(85, 10)))
                events.append((t + 100, 'off', self.KICK, 0))
            
            # 2. Snare/Rimshot - 'Atrás do tempo' (laid back)
            for b in [1, 3]:
                # Rimshot no 2, Snare no 4 (ou vice-versa)
                drum = self.RIMSHOT if b == 1 else self.SNARE
                t = int(m_offset + b * ticks_per_beat) + random.randint(15, 45) # Sempre um pouco atrasado
                events.append((t, 'on', drum, self._humanize_velocity(75, 15)))
                events.append((t + 120, 'off', drum, 0))
                
                # Ghost notes (Notas fantasma) muito leves
                if random.random() < 0.3:
                    ghost_t = t + int(ticks_per_beat * 0.5)
                    events.append((ghost_t, 'on', self.SNARE, self._humanize_velocity(25, 5)))
                    events.append((ghost_t + 80, 'off', self.SNARE, 0))
            
            # 3. Hi-hat (Contratempo) - O coração do Swing
            for b in range(4):
                # Cabeça do tempo (mais forte)
                t1 = m_offset + b * ticks_per_beat + self._humanize_time(10)
                events.append((max(0, t1), 'on', self.CLOSED_HH, self._humanize_velocity(65, 12)))
                events.append((t1 + 80, 'off', self.CLOSED_HH, 0))
                
                # Contratempo com Swing (mais fraco)
                t2 = m_offset + b * ticks_per_beat + int(ticks_per_beat * self.swing) + self._humanize_time(10)
                events.append((t2, 'on', self.CLOSED_HH, self._humanize_velocity(40, 10)))
                events.append((t2 + 80, 'off', self.CLOSED_HH, 0))

        events.sort()
        last_tick = 0
        for tick, type, note, vel in events:
            delta = tick - last_tick
            track.append(Message('note_on' if type == 'on' else 'note_off', 
                                 note=note, velocity=vel, time=delta, channel=9))
            last_tick = tick
        return track
