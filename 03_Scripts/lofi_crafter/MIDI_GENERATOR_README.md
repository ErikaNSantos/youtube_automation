# Gerador de Músicas Lo-Fi em MIDI

Sistema completo e modular para geração de músicas Lo-Fi em formato MIDI, com suporte a múltiplos estilos, humanização avançada e padrões rítmicos autênticos.

## 📋 Características

### ✨ Funcionalidades Principais

- **Geração de Harmonia**: Progressões de acordes típicas de Lo-Fi e Jazz (acordes com 7ª, 9ª, progressões ii-V-I)
- **Geração de Melodia**: Melodias orgânicas baseadas nas progressões harmônicas
- **Sistema de Bateria**: Padrões rítmicos autênticos com groove Lo-Fi
- **Humanização Avançada**: Variação de timing e velocity para som natural e não-robótico
- **Swing Configurável**: Hi-hat com swing acentuado (groove de tercina)
- **6 Estilos Diferentes**: Chillhop, Jazzhop, Sleep, Ambient, Sad e Nostalgic

### 🎵 Estilos Disponíveis

1. **Chillhop**: Foco em samples de piano, baixos marcados e beats consistentes (75-90 BPM)
2. **Jazzhop**: Progressões jazzísticas complexas com swing acentuado (80-95 BPM)
3. **Sleep/Ambient Lo-Fi**: Andamento lento, bateria sutil, acordes sustentados (60-70 BPM)
4. **Ambient Lo-Fi**: Atmosférico, foco em texturas e pads (60-70 BPM)
5. **Sad Lo-Fi**: Progressões em tons menores, melodias melancólicas (70-80 BPM)
6. **Nostalgic Lo-Fi**: Melodias espaçadas e emotivas (70-80 BPM)

## 🏗️ Arquitetura

O sistema é composto por três módulos principais:

```
lofi_crafter/
├── midi_generator.py    # Geração de harmonia e melodia
├── drum_generator.py    # Geração de bateria e percussão
├── lofi_engine.py       # Motor principal (consolida tudo)
└── output/              # Diretório de saída dos arquivos MIDI
```

### Módulos

#### `midi_generator.py`
- Classe `LofiMidiGenerator`: Gera harmonia e melodia
- Progressões harmônicas configuráveis
- Humanização de timing e velocity
- Suporte a diferentes escalas (maior, menor, dórica)

#### `drum_generator.py`
- Classe `DrumGenerator`: Gera padrões de bateria
- Kick com batidas fora do tempo (groove orgânico)
- Snare/Rimshot cravado nos tempos 2 e 4
- Hi-hat com swing configurável
- Humanização específica para percussão

#### `lofi_engine.py`
- Classe `LofiEngine`: Motor principal
- Sistema modular de presets de estilo
- Interface de linha de comando
- Geração em lote e variações

## 🚀 Instalação

### Dependências

```bash
pip install mido
```

### Estrutura de Arquivos

Certifique-se de que os três arquivos Python estejam no mesmo diretório:
- `midi_generator.py`
- `drum_generator.py`
- `lofi_engine.py`

## 📖 Uso

### Interface de Linha de Comando

#### Listar Estilos Disponíveis

```bash
python lofi_engine.py --list
```

#### Gerar Todos os Estilos

```bash
python lofi_engine.py --all --measures 16
```

#### Gerar Estilo Específico

```bash
python lofi_engine.py --style chillhop --key C --bpm 85 --measures 16
```

#### Gerar Variações de um Estilo

```bash
python lofi_engine.py --style jazzhop --variations 5 --measures 8
```

#### Gerar Sem Bateria

```bash
python lofi_engine.py --style sad --key Am --no-drums --measures 16
```

### Parâmetros Disponíveis

| Parâmetro | Descrição | Exemplo |
|-----------|-----------|---------|
| `--style` | Estilo de Lo-Fi | `chillhop`, `jazzhop`, `sleep`, `ambient`, `sad`, `nostalgic` |
| `--key` | Tonalidade | `C`, `Am`, `F#`, `Bbm` |
| `--bpm` | Batidas por minuto | `80`, `72`, `90` |
| `--measures` | Número de compassos | `8`, `16`, `32` |
| `--no-drums` | Gerar sem bateria | (flag) |
| `--output` | Diretório de saída | `./output`, `./my_tracks` |
| `--all` | Gerar todos os estilos | (flag) |
| `--variations` | Número de variações | `3`, `5`, `10` |
| `--list` | Listar estilos | (flag) |

### Uso Programático (Python)

```python
from lofi_engine import LofiEngine, LofiStyle

# Criar engine
engine = LofiEngine(output_dir='./my_output')

# Gerar faixa específica
engine.generate_track(
    style=LofiStyle.CHILLHOP,
    key='C',
    bpm=85,
    measures=16,
    include_drums=True
)

# Gerar todos os estilos
engine.generate_all_styles(measures=8)

# Gerar variações
engine.generate_variations(
    style=LofiStyle.JAZZHOP,
    count=5,
    measures=16
)
```

## 🎹 Detalhes Técnicos

### Progressões Harmônicas

O sistema implementa as seguintes progressões:

- **ii-V-I**: Progressão jazzística clássica
- **I-vi-ii-V**: Progressão circular popular
- **vi-ii-V-I**: Variação com início no relativo menor
- **I-IV-vi-V**: Progressão pop/rock adaptada
- **Sad Progression**: vi-IV-I-V (melancólica)
- **Nostalgic**: I-iii-vi-ii (emotiva)

### Qualidades de Acordes

- Major7, Minor7, Dominant7
- Minor7b5 (Half-diminished)
- Major9, Minor9, Dominant9
- Major6, Minor6

### Humanização

#### Timing
- Variação de ±5-8% no timing das notas
- Aplicação de swing configurável no hi-hat
- Deslocamento sutil nas notas de acordes

#### Velocity
- Variação de ±15-20% na velocidade das notas
- Acentuação em tempos fortes
- Ghost notes com velocidade reduzida

### Bateria (Canal MIDI 10)

#### Mapeamento General MIDI
- **Kick (36)**: Bass Drum 1
- **Snare (38)**: Acoustic Snare
- **Rimshot (37)**: Side Stick
- **Closed Hi-Hat (42)**
- **Open Hi-Hat (46)**

#### Padrões Rítmicos

**Chillhop/Jazzhop:**
- Kick com batidas fora do tempo (groove orgânico)
- Snare/Rimshot cravado nos tempos 2 e 4
- Hi-hat com swing 55-67%

**Sleep/Ambient:**
- Kick minimalista (tempos 1 e 3)
- Rimshot suave ou ausente
- Hi-hat ausente ou muito sutil

**Sad/Nostalgic:**
- Padrão simples com variações
- Swing sutil (52-58%)
- Rimshot predominante

## 📊 Exemplos de Saída

Após executar `python lofi_engine.py --all --measures 8`, os seguintes arquivos são gerados:

```
output/
├── lofi_chillhop_Cm_80bpm.mid          (1.7K)
├── lofi_jazzhop_Ebm_93bpm.mid          (1.7K)
├── lofi_sleep_ambient_lo-fi_Am_60bpm.mid (828B)
├── lofi_ambient_lo-fi_Em_60bpm.mid     (853B)
├── lofi_sad_lo-fi_Am_76bpm.mid         (1.6K)
└── lofi_nostalgic_lo-fi_Dm_76bpm.mid   (1.6K)
```

## 🔧 Configuração e Extensão

### Adicionar Novo Estilo

Edite `lofi_engine.py` e adicione um novo preset em `STYLE_PRESETS`:

```python
LofiStyle.CUSTOM: {
    'name': 'Custom Style',
    'description': 'Descrição do estilo',
    'bpm_range': (70, 85),
    'key_preferences': ['C', 'G', 'D'],
    'mode': 'major',
    'measures': 16,
    'has_drums': True,
    'drum_intensity': 'medium',
}
```

### Adicionar Nova Progressão

Edite `midi_generator.py` e adicione em `CHORD_PROGRESSIONS`:

```python
'my_progression': [
    (1, ChordQuality.MAJOR7),
    (4, ChordQuality.MAJOR7),
    (5, ChordQuality.DOMINANT7),
    (1, ChordQuality.MAJOR7)
]
```

## 🎯 Casos de Uso

### Produção Musical
- Base para composições Lo-Fi
- Referência harmônica e melódica
- Protótipos rápidos de ideias

### Educação Musical
- Estudo de progressões harmônicas
- Análise de padrões rítmicos
- Compreensão de humanização

### Desenvolvimento de Jogos/Apps
- Música procedural
- Trilhas sonoras dinâmicas
- Geração de conteúdo

### Automação de Conteúdo
- Geração em massa de faixas
- Criação de bibliotecas musicais
- Integração com pipelines de vídeo

## 📝 Notas Técnicas

### Formato MIDI
- **Ticks per beat**: 480 (alta resolução)
- **Time signature**: 4/4
- **Canais**: 0 (Harmonia), 1 (Melodia), 9 (Bateria)
- **Programs**: 0 (Piano), 1 (Piano Brilhante)

### BPM e Timing
- BPM definido via MetaMessage 'set_tempo'
- Humanização aplicada em ticks
- Swing calculado como offset de subdivisão

### Compatibilidade
- Arquivos compatíveis com qualquer DAW (Ableton, FL Studio, Logic, etc.)
- Formato General MIDI padrão
- Editável em qualquer editor MIDI

## 🐛 Troubleshooting

### Arquivo não toca no meu software
- Certifique-se de que o software suporta MIDI
- Verifique se os canais estão mapeados corretamente
- Confirme que o canal 10 está configurado para bateria

### Bateria não soa corretamente
- Verifique se o instrumento no canal 10 é um kit de bateria
- Confirme o mapeamento General MIDI
- Alguns softwares requerem configuração manual do canal de bateria

### Sons muito robóticos
- Aumente a quantidade de humanização nos parâmetros
- Ajuste o swing amount
- Gere múltiplas variações e escolha a melhor

## 🤝 Contribuindo

Para contribuir com o projeto:

1. Faça fork do repositório
2. Crie uma branch de feature (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'feat: adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a mesma licença do repositório principal.

## ✨ Créditos

Desenvolvido como extensão do projeto Lofi Crafter, integrando geração MIDI nativa ao pipeline de automação de conteúdo.

---

**Versão**: 1.0.0  
**Data**: Fevereiro 2026  
**Autor**: Equipe de Desenvolvimento
