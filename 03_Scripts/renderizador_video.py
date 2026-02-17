import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path
import subprocess
import time
import numpy as np
import cv2 
from proglog import ProgressBarLogger

# --- IMPORTS MOVIEPY 2.2.1 ---
from moviepy import (
    VideoFileClip, ImageClip, AudioFileClip, TextClip, ColorClip, 
    CompositeVideoClip, concatenate_videoclips, vfx
)

# ✅ Blur via OpenCV
def aplicar_blur_opencv(frame):
    return cv2.GaussianBlur(frame, (61, 61), 10)

class MugiwaraLogger(ProgressBarLogger):
    def __init__(self, app):
        super().__init__()
        self.app = app

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars[bar]['total']
        percentage = value / total
        self.app.after(0, lambda: self.app.atualizar_barra(percentage, bar))

class AppVideoMaker(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("👒 Mugiwara Maker v1.7.4 - Auto-Fit Text")
        self.geometry("600x900")
        
        self.script_path = Path(__file__).parent
        self.root_path = self.script_path.parent
        self.assets_path = self.root_path / "01_Assets"
        self.raw_path = self.root_path / "02_Raw_Material"
        self.prod_path = self.root_path / "04_Production"
        
        self.logo_path = self.assets_path / "logos" / "logo_branco.png"
        self.font_path = self.buscar_fonte()
        
        self.bg_path = ctk.StringVar()
        self.audio_path = ctk.StringVar()
        self.status_msg = ctk.StringVar(value="Correção de quebra de texto aplicada.")
        self.criar_layout()

    def buscar_fonte(self):
        fonts = list((self.assets_path / "fonts").glob("*Alibaba*BoldItalic*.*"))
        return str(fonts[0].absolute()) if fonts else "BPreplay"

    def criar_layout(self):
        ctk.CTkLabel(self, text="Mugiwara Production Hub", font=("BPreplay", 24, "bold")).pack(pady=15)
        
        ctk.CTkLabel(self, text="Formato de Destino:", font=("BPreplay", 12)).pack()
        self.formato_var = ctk.StringVar(value="YouTube Longo (16:9)")
        self.combo_formato = ctk.CTkComboBox(self, values=["YouTube Longo (16:9)", "Shorts/Reels (9:16)"], 
                                             variable=self.formato_var, width=300)
        self.combo_formato.pack(pady=5)

        ctk.CTkButton(self, text="📁 Selecionar Vídeo (Raw)", command=self.sel_bg).pack(pady=5)
        ctk.CTkLabel(self, textvariable=self.bg_path, font=("BPreplay", 10), wraplength=500).pack()
        
        ctk.CTkButton(self, text="🎵 Selecionar Beat (LoFi)", command=self.sel_audio).pack(pady=5)
        ctk.CTkLabel(self, textvariable=self.audio_path, font=("BPreplay", 10), wraplength=500).pack()

        self.entry_frase = ctk.CTkEntry(self, placeholder_text="Frase em Inglês...", width=450)
        self.entry_frase.pack(pady=15)

        self.progress_bar = ctk.CTkProgressBar(self, width=400)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)
        ctk.CTkLabel(self, textvariable=self.status_msg, font=("BPreplay", 12, "italic")).pack()

        self.btn_gerar = ctk.CTkButton(self, text="🚀 1. RENDERIZAR (CPU STABLE)", fg_color="#2c3e50", command=self.start_render)
        self.btn_gerar.pack(pady=10)

        ctk.CTkLabel(self, text="──────────────────────────────", text_color="gray").pack()
        self.combo_longo = ctk.CTkComboBox(self, values=["1h", "4h", "10h"])
        self.combo_longo.set("1h")
        self.combo_longo.pack(pady=5)
        self.btn_concat = ctk.CTkButton(self, text="🔗 2. CONCATENAR FINAL", fg_color="#d35400", command=self.start_concat)
        self.btn_concat.pack(pady=10)

    def sel_bg(self): 
        pasta = "shorts" if "9:16" in self.formato_var.get() else "visuals"
        self.bg_path.set(filedialog.askopenfilename(initialdir=self.raw_path / pasta))

    def sel_audio(self): 
        self.audio_path.set(filedialog.askopenfilename(initialdir=self.raw_path / "audios"))

    def atualizar_barra(self, valor, etapa):
        self.progress_bar.set(valor)
        self.status_msg.set(f"Processando... ({int(valor*100)}%)")

    def start_render(self):
        if not self.bg_path.get() or not self.audio_path.get():
            messagebox.showwarning("Aviso", "Selecione os ativos!")
            return
        threading.Thread(target=self.executar_render, daemon=True).start()

    def executar_render(self):
        try:
            is_short = "9:16" in self.formato_var.get()
            
            audio = AudioFileClip(self.audio_path.get()).with_volume_scaled(0.4)
            if is_short and audio.duration > 59:
                duracao = 59
                audio = audio.subclipped(0, duracao)
            else:
                duracao = audio.duration
            
            tempo_intro = 5

            bg_clip = VideoFileClip(self.bg_path.get()).without_audio()
            if is_short:
                bg_clip = bg_clip.resized(height=1920) 
            else:
                bg_clip = bg_clip.resized(height=720)

            n_loops = int(duracao / bg_clip.duration) + 1
            video_base = concatenate_videoclips([bg_clip] * n_loops).with_duration(duracao)
            
            # Filtro escuro (mantido em 70%)
            filtro = ColorClip(size=video_base.size, color=(0,0,0)).with_duration(duracao).with_opacity(0.7)
            
            video_intro = video_base.subclipped(0, tempo_intro).image_transform(aplicar_blur_opencv)
            video_resto = video_base.subclipped(tempo_intro, duracao)
            video_final_bg = concatenate_videoclips([video_intro, video_resto])

            logo_width = 350 if is_short else 280
            logo = (ImageClip(str(self.logo_path)).resized(width=logo_width)
                    .with_duration(tempo_intro).with_position('center').with_effects([vfx.FadeOut(duration=1)]))

            frase = self.entry_frase.get()
            
            # ✅ SOLUÇÃO DEFINITIVA PARA CORTES: Auto-Fit
            # Definimos uma "caixa segura" (90% largura, 80% altura)
            box_w = int(video_base.w * 0.90)
            box_h = int(video_base.h * 0.80)

            if is_short:
                # Para Shorts: NÃO definimos font_size.
                # Passamos a largura E altura da caixa. O MoviePy calcula a melhor fonte.
                txt = TextClip(text=frase, color='white', font=self.font_path,
                               method='caption', size=(box_w, box_h), 
                               text_align='center')
            else:
                # Para Longo: Mantemos o padrão que funcionava, só ajustando a largura
                txt = TextClip(text=frase, font_size=32, color='white', font=self.font_path,
                               method='caption', size=(box_w, None), 
                               text_align='center')

            txt = txt.with_start(tempo_intro).with_duration(duracao - tempo_intro).with_position('center')

            final = CompositeVideoClip([video_final_bg, filtro, logo, txt]).with_audio(audio)
            
            tipo_pasta = "shorts" if is_short else "long_form"
            out_path = self.prod_path / tipo_pasta
            out_path.mkdir(parents=True, exist_ok=True)
            self.last_video = out_path / f"render_{int(time.time())}.mp4"
            
            # Encoder seguro (CPU)
            final.write_videofile(
                str(self.last_video), fps=8, codec="libx264", 
                threads=4, preset="ultrafast", logger=MugiwaraLogger(self)
            )
            
            messagebox.showinfo("Sucesso", f"Vídeo salvo em {tipo_pasta} com texto ajustado!")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha na produção: {e}")

    def start_concat(self):
        if not self.last_video or not self.last_video.exists():
            messagebox.showwarning("Aviso", "Gere o bloco base primeiro!")
            return
        threading.Thread(target=self.executar_concat, daemon=True).start()

    def executar_concat(self):
        try:
            self.status_msg.set("Concatenando via FFmpeg...")
            target = self.combo_longo.get()
            horas = int(target.replace("h", ""))
            clip_temp = VideoFileClip(str(self.last_video))
            n_reps = int((horas * 3600) / clip_temp.duration)
            clip_temp.close()

            list_path = self.root_path / "temp_list.txt"
            output_final = self.prod_path / "long_form" / f"video_{target}_{int(time.time())}.mp4"

            with open(list_path, "w") as f:
                for _ in range(n_reps): f.write(f"file '{self.last_video.name}'\n")

            cmd = ['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', str(list_path), '-c', 'copy', str(output_final)]
            subprocess.run(cmd, cwd=str(self.last_video.parent), check=True)
            list_path.unlink()
            messagebox.showinfo("Sucesso", f"Vídeo de {target} concluído!")
            self.status_msg.set("Pronto!")
        except Exception as e:
            messagebox.showerror("Erro FFmpeg", str(e))

if __name__ == "__main__":
    AppVideoMaker().mainloop()