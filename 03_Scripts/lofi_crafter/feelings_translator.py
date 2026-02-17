import scipy.io.wavfile
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import sys
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
import threading
import datetime
import time

def compor_musica(sentimento, duracao_segundos, quantidade, label_status, botao_gerar):
    try:
        label_status.config(text="Status: A carregar a IA na memória...", fg="orange")
        botao_gerar.config(state="disabled")
        
        # Carrega o modelo pesado apenas UMA VEZ antes do loop começar
        processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
        model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")
        
        pasta_atual = Path(__file__).parent.resolve()
        
        # Marca o tempo de início de todo o lote
        inicio_lote = time.time()
        
        # Inicia a produção em batelada
        for i in range(quantidade):
            label_status.config(text=f"Status: A renderizar áudio {i+1} de {quantidade}...", fg="blue")
            
            inputs = processor(
                text=[sentimento],
                padding=True,
                return_tensors="pt",
            )
            
            tokens = int((duracao_segundos / 5) * 256)
            
            # --- INÍCIO DO CRONÔMETRO DA FAIXA ---
            inicio_faixa = time.time()
            
            # do_sample=True é o segredo para a IA não gerar a mesma música repetida
            # guidance_scale=4.5 mantém a IA focada no seu prompt
            audio_values = model.generate(**inputs, max_new_tokens=tokens, do_sample=True, guidance_scale=4.5, temperature=0.7)
            
            # --- FIM DO CRONÔMETRO DA FAIXA ---
            fim_faixa = time.time()
            tempo_faixa = fim_faixa - inicio_faixa
            
            # Formata o tempo da faixa para ficar bonitinho no terminal (ex: 1m 15s ou 45.5s)
            minutos_faixa = int(tempo_faixa // 60)
            segundos_faixa = int(tempo_faixa % 60)
            tempo_formatado = f"{minutos_faixa}m {segundos_faixa}s" if minutos_faixa > 0 else f"{tempo_faixa:.1f}s"
            
            taxa_amostragem = model.config.audio_encoder.sampling_rate
            dados_audio = audio_values[0, 0].numpy()
            
            # Cria um nome único com timestamp para não sobrescrever os arquivos
            timestamp = datetime.datetime.now().strftime("%H%M%S")
            caminho_saida = pasta_atual / f"trilha_lofi_vibe_{i+1}_{timestamp}.wav"
            
            scipy.io.wavfile.write(str(caminho_saida), rate=taxa_amostragem, data=dados_audio)
            
            # Agora o terminal mostra o tempo exato que levou para gerar!
            print(f"Áudio {i+1} guardado! (Tempo de geração: {tempo_formatado}) -> {caminho_saida}")
            
        # Calcula o tempo total que o lote inteiro demorou
        fim_lote = time.time()
        tempo_total_lote = fim_lote - inicio_lote
        minutos_totais = int(tempo_total_lote // 60)
        segundos_totais = int(tempo_total_lote % 60)
            
        label_status.config(text=f"Status: Sucesso! {quantidade} áudios gerados.", fg="green")
        
        # Mostra o tempo total na caixinha final
        mensagem_final = (
            f"A produção terminou!\n"
            f"Foram guardadas {quantidade} músicas na sua pasta.\n\n"
            f"⏱️ Tempo total de processamento: {minutos_totais}m e {segundos_totais}s"
        )
        messagebox.showinfo("Lote Finalizado", mensagem_final)
        
    except Exception as e:
        label_status.config(text="Status: Erro na geração.", fg="red")
        messagebox.showerror("Erro", f"Ocorreu um erro:\n{str(e)}")
    finally:
        botao_gerar.config(state="normal")

def iniciar_geracao():
    sentimento = entrada_sentimento.get()
    try:
        duracao = int(entrada_duracao.get())
        quantidade = int(entrada_quantidade.get())
    except ValueError:
        messagebox.showwarning("Aviso", "Duração e Quantidade têm de ser números (ex: 15 e 5).")
        return
        
    if not sentimento.strip():
        messagebox.showwarning("Aviso", "Por favor, descreva o sentimento ou estilo da música.")
        return

    # Inicia o processamento em background
    thread = threading.Thread(target=compor_musica, args=(sentimento, duracao, quantidade, label_status, botao_gerar))
    thread.daemon = True
    thread.start()

# ==========================================
# INTERFACE GRÁFICA DA MÁQUINA DE LOTE
# ==========================================
janela = tk.Tk()
janela.title("Mugiwara Lofi Composer - Lote")
janela.geometry("450x360")
janela.configure(padx=20, pady=20)

tk.Label(janela, text="🎶 Gerador de Áudio Lofi (Lote)", font=("BPreplay", 12, "bold")).pack(pady=(0, 15))

# Campo Sentimento
tk.Label(janela, text="Descreva o estilo (sem pedir chuva/ruídos):", font=("BPreplay", 10)).pack(anchor="w")
entrada_sentimento = tk.Entry(janela, width=50)
entrada_sentimento.insert(0, "sad lofi hip hop beat, melancholic piano chords, deep bass, chill drum loop, 80 bpm")
entrada_sentimento.pack(pady=5)

# Campo Duração
tk.Label(janela, text="Duração de cada faixa (segundos):", font=("BPreplay", 10)).pack(anchor="w", pady=(10, 0))
entrada_duracao = tk.Entry(janela, width=15)
entrada_duracao.insert(0, "30")
entrada_duracao.pack(anchor="w", pady=5)

# Campo Quantidade
tk.Label(janela, text="Quantas músicas gerar?", font=("BPreplay", 12, "bold"), fg="#333").pack(anchor="w", pady=(10, 0))
entrada_quantidade = tk.Entry(janela, width=15)
entrada_quantidade.insert(0, "5")
entrada_quantidade.pack(anchor="w", pady=5)

# Botão Gerar
botao_gerar = tk.Button(janela, text="Iniciar Produção em Lote", command=iniciar_geracao, bg="#4CAF50", fg="white", font=("BPreplay", 10, "bold"), pady=5, padx=10)
botao_gerar.pack(pady=15)

label_status = tk.Label(janela, text="Status: Aguardando...", font=("BPreplay", 9, "italic"), fg="gray")
label_status.pack()

janela.mainloop()