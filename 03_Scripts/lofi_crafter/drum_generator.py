"""
Gerador de Bateria e Percussão Lo-Fi
Implementa padrões rítmicos com groove, swing e humanização
"""

import random
from mido import MidiFile, MidiTrack, Message, MetaMessage
from typing import List, Dict, Tuple
from midi_generator import LofiStyle


class DrumGenerator:
    """Gerador de padrões de bateria Lo-Fi"""
    
    # Mapeamento General MIDI de bateria (Canal 10)
    KICK = 36          # Bass Drum 1
    SNARE = 38         # Acoustic Snare
    RIMSHOT = 37       # Side Stick
    CLOSED_HH = 42     # Closed Hi-Hat
    OPEN_HH = 46       # Open Hi-Hat
    CRASH = 49         # Crash Cymbal 1
    RIDE = 51          # Ride Cymbal 1
    
    def __init__(self, style: LofiStyle, bpm: int):
        """
        Inicializa o gerador de bateria
        
        Args:
            style: Estilo de Lo-Fi
            bpm: Batidas por minuto
        """
        self.style = style
        self.bpm = bpm
        self.swing_amount = self._get_swing_amount()
        
    def _get_swing_amount(self) -> float:
        """Retorna quantidade de swing baseada no estilo"""
        if self.style in [LofiStyle.CHILLHOP, LofiStyle.JAZZHOP]:
            return random.uniform(0.55, 0.67)  # Swing médio a forte
        elif self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]:
            return 0.5  # Sem swing
        else:  # SAD, NOSTALGIC
            return random.uniform(0.52, 0.58)  # Swing sutil
    
    def _humanize_timing(self, base_time: int, amount: float = 0.08) -> int:
        """
        Aplica humanização ao timing da bateria
        
        Args:
            base_time: Tempo base em ticks
            amount: Quantidade de humanização
        
        Returns:
            Tempo humanizado
        """
        variation = int(base_time * amount * random.uniform(-1, 1))
        return max(0, base_time + variation)
    
    def _humanize_velocity(self, base_velocity: int, amount: float = 0.2) -> int:
        """
        Aplica humanização à velocidade
        
        Args:
            base_velocity: Velocidade base
            amount: Quantidade de humanização
        
        Returns:
            Velocidade humanizada
        """
        variation = int(base_velocity * amount * random.uniform(-0.5, 1.0))
        return max(20, min(127, base_velocity + variation))
    
    def _apply_swing(self, position: int, subdivision: int, ticks_per_subdivision: int) -> int:
        """
        Aplica swing ao timing
        
        Args:
            position: Posição na subdivisão (0, 1, 2, 3...)
            subdivision: Subdivisão total
            ticks_per_subdivision: Ticks por subdivisão
        
        Returns:
            Offset de tempo para aplicar swing
        """
        # Aplica swing apenas nas notas off-beat (posições ímpares)
        if position % 2 == 1 and self.swing_amount > 0.5:
            swing_offset = int(ticks_per_subdivision * (self.swing_amount - 0.5) * 2)
            return swing_offset
        return 0
    
    def _generate_kick_pattern(self, ticks_per_beat: int, beats: int = 4) -> List[Tuple[int, int]]:
        """
        Gera padrão de bumbo (kick)
        
        Args:
            ticks_per_beat: Ticks por batida
            beats: Número de batidas no compasso
        
        Returns:
            Lista de (tempo_em_ticks, velocity)
        """
        pattern = []
        
        if self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]:
            # Padrão minimalista - apenas tempos 1 e 3
            base_velocity = 50
            pattern.append((0, self._humanize_velocity(base_velocity)))
            pattern.append((ticks_per_beat * 2, self._humanize_velocity(base_velocity - 5)))
            
        elif self.style in [LofiStyle.SAD, LofiStyle.NOSTALGIC]:
            # Padrão simples com variação
            base_velocity = 65
            pattern.append((0, self._humanize_velocity(base_velocity)))
            pattern.append((ticks_per_beat * 2, self._humanize_velocity(base_velocity - 5)))
            
            # Adiciona kick sincopado ocasionalmente
            if random.random() < 0.4:
                pattern.append((ticks_per_beat * 3 + ticks_per_beat // 2, 
                              self._humanize_velocity(base_velocity - 10)))
        
        else:  # CHILLHOP, JAZZHOP
            # Padrão com kicks fora do tempo (groove orgânico)
            base_velocity = 75
            
            # Kick no tempo 1 (forte)
            pattern.append((0, self._humanize_velocity(base_velocity)))
            
            # Kick sincopado antes do tempo 2
            offset = random.randint(-ticks_per_beat // 8, ticks_per_beat // 8)
            pattern.append((ticks_per_beat + offset, 
                          self._humanize_velocity(base_velocity - 10)))
            
            # Kick no tempo 3
            pattern.append((ticks_per_beat * 2, self._humanize_velocity(base_velocity - 5)))
            
            # Kick sincopado ocasional
            if random.random() < 0.6:
                offset = random.randint(-ticks_per_beat // 6, ticks_per_beat // 6)
                pattern.append((ticks_per_beat * 3 + ticks_per_beat // 2 + offset, 
                              self._humanize_velocity(base_velocity - 15)))
        
        return pattern
    
    def _generate_snare_pattern(self, ticks_per_beat: int, beats: int = 4) -> List[Tuple[int, int, int]]:
        """
        Gera padrão de caixa/rimshot
        
        Args:
            ticks_per_beat: Ticks por batida
            beats: Número de batidas
        
        Returns:
            Lista de (tempo_em_ticks, nota, velocity)
        """
        pattern = []
        
        if self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]:
            # Padrão muito sutil ou ausente
            if random.random() < 0.5:
                base_velocity = 35
                # Apenas rimshot suave no tempo 3
                pattern.append((ticks_per_beat * 2, self.RIMSHOT, 
                              self._humanize_velocity(base_velocity)))
        
        elif self.style in [LofiStyle.SAD, LofiStyle.NOSTALGIC]:
            # Rimshot no tempo 2 e 4
            base_velocity = 55
            pattern.append((ticks_per_beat, self.RIMSHOT, 
                          self._humanize_velocity(base_velocity)))
            pattern.append((ticks_per_beat * 3, self.RIMSHOT, 
                          self._humanize_velocity(base_velocity - 5)))
        
        else:  # CHILLHOP, JAZZHOP
            # Snare/Rimshot cravado no tempo 2 e 4
            base_velocity = 70
            
            # Usa mix de snare e rimshot
            use_rimshot = random.random() < 0.6
            drum = self.RIMSHOT if use_rimshot else self.SNARE
            
            # Tempo 2 (cravado)
            pattern.append((ticks_per_beat, drum, 
                          self._humanize_velocity(base_velocity)))
            
            # Tempo 4 (cravado)
            pattern.append((ticks_per_beat * 3, drum, 
                          self._humanize_velocity(base_velocity + 5)))
            
            # Ghost notes ocasionais
            if random.random() < 0.4:
                ghost_time = ticks_per_beat // 2
                pattern.append((ghost_time, drum, 
                              self._humanize_velocity(base_velocity - 35)))
        
        return pattern
    
    def _generate_hihat_pattern(self, ticks_per_beat: int, beats: int = 4) -> List[Tuple[int, int, int]]:
        """
        Gera padrão de hi-hat com swing
        
        Args:
            ticks_per_beat: Ticks por batida
            beats: Número de batidas
        
        Returns:
            Lista de (tempo_em_ticks, nota, velocity)
        """
        pattern = []
        
        if self.style in [LofiStyle.SLEEP, LofiStyle.AMBIENT]:
            # Hi-hat minimalista ou ausente
            if random.random() < 0.3:
                base_velocity = 30
                for beat in range(beats):
                    pattern.append((ticks_per_beat * beat, self.CLOSED_HH, 
                                  self._humanize_velocity(base_velocity)))
            return pattern
        
        # Para outros estilos, gera padrão com swing
        subdivision = 8  # Colcheias
        ticks_per_subdivision = ticks_per_beat // 2
        
        base_velocity = 50 if self.style in [LofiStyle.SAD, LofiStyle.NOSTALGIC] else 60
        
        for i in range(beats * 2):  # 2 subdivisões por beat (colcheias)
            time = i * ticks_per_subdivision
            
            # Aplica swing
            swing_offset = self._apply_swing(i, subdivision, ticks_per_subdivision)
            time += swing_offset
            
            # Humaniza timing
            time = self._humanize_timing(time, amount=0.05)
            
            # Varia velocidade (acentua tempos fortes)
            if i % 4 == 0:  # Tempo 1 e 3
                velocity = self._humanize_velocity(base_velocity + 15)
            elif i % 2 == 0:  # Tempo 2 e 4
                velocity = self._humanize_velocity(base_velocity + 8)
            else:  # Contratempos
                velocity = self._humanize_velocity(base_velocity - 5)
            
            # Ocasionalmente abre o hi-hat
            if random.random() < 0.1 and i % 2 == 1:
                pattern.append((time, self.OPEN_HH, velocity))
            else:
                pattern.append((time, self.CLOSED_HH, velocity))
        
        return pattern
    
    def generate_drum_track(self, mid: MidiFile, measures: int = 8) -> MidiTrack:
        """
        Gera track completa de bateria
        
        Args:
            mid: Arquivo MIDI
            measures: Número de compassos
        
        Returns:
            Track MIDI de bateria
        """
        track = MidiTrack()
        ticks_per_beat = mid.ticks_per_beat
        ticks_per_measure = ticks_per_beat * 4  # Compasso 4/4
        
        # Configurações iniciais
        track.append(MetaMessage('track_name', name='Drums', time=0))
        
        # Canal 10 é o canal de bateria no General MIDI
        # Program change não é necessário para canal de bateria
        
        # Gera padrões para cada compasso
        all_events = []
        
        for measure in range(measures):
            measure_offset = measure * ticks_per_measure
            
            # Gera padrões
            kick_pattern = self._generate_kick_pattern(ticks_per_beat)
            snare_pattern = self._generate_snare_pattern(ticks_per_beat)
            hihat_pattern = self._generate_hihat_pattern(ticks_per_beat)
            
            # Adiciona eventos de kick
            for time, velocity in kick_pattern:
                all_events.append((measure_offset + time, 'note_on', self.KICK, velocity))
                all_events.append((measure_offset + time + 100, 'note_off', self.KICK, 0))
            
            # Adiciona eventos de snare/rimshot
            for time, note, velocity in snare_pattern:
                all_events.append((measure_offset + time, 'note_on', note, velocity))
                all_events.append((measure_offset + time + 150, 'note_off', note, 0))
            
            # Adiciona eventos de hi-hat
            for time, note, velocity in hihat_pattern:
                all_events.append((measure_offset + time, 'note_on', note, velocity))
                all_events.append((measure_offset + time + 80, 'note_off', note, 0))
        
        # Ordena eventos por tempo
        all_events.sort(key=lambda x: x[0])
        
        # Converte para mensagens MIDI com delta time
        current_time = 0
        for abs_time, event_type, note, velocity in all_events:
            delta_time = abs_time - current_time
            
            if event_type == 'note_on':
                track.append(Message('note_on', note=note, velocity=velocity, 
                                    time=delta_time, channel=9))  # Canal 9 = Canal 10 (0-indexed)
            else:
                track.append(Message('note_off', note=note, velocity=velocity, 
                                    time=delta_time, channel=9))
            
            current_time = abs_time
        
        return track


if __name__ == "__main__":
    # Teste básico
    from mido import MidiFile, MetaMessage
    import mido
    
    mid = MidiFile(ticks_per_beat=480)
    
    # Track de tempo
    tempo_track = MidiTrack()
    mid.tracks.append(tempo_track)
    tempo_track.append(MetaMessage('set_tempo', tempo=mido.bpm2tempo(85), time=0))
    
    # Gera bateria
    drum_gen = DrumGenerator(style=LofiStyle.CHILLHOP, bpm=85)
    drum_track = drum_gen.generate_drum_track(mid, measures=4)
    mid.tracks.append(drum_track)
    
    mid.save('test_drums.mid')
    print("Arquivo de teste de bateria gerado: test_drums.mid")
