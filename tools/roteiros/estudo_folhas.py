"""Folhas de contato dos maiores vídeos de um player: o que aparece na tela, e quando.

A transcrição só pega a fala. Este passo mostra o resto: quanto é rosto, quanto é tela,
quando entra a inserção, se tem título fixo, como é o primeiro quadro.
Baixa cada vídeo, gera uma folha (16 quadros espaçados, 8×2) e APAGA o vídeo (disco).

uso:   python tools/roteiros/estudo_folhas.py <pasta> [--top 6]
saída: tools/roteiros/work/estudo/<usuario>/folhas/folha-<shortCode>.png  (+ passo entre quadros no terminal)
"""
import argparse, json, os, shutil, subprocess, sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PLAYERS = os.path.join(RAIZ, "docs", "conteudo", "banco-roteiros", "players")
WORK = os.path.join(os.path.dirname(os.path.abspath(__file__)), "work", "estudo")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--top", type=int, default=6)
    a = ap.parse_args()
    base = os.path.join(PLAYERS, a.pasta)
    usuario = json.load(open(os.path.join(base, "resumo.json"), encoding="utf-8"))["usuario"]
    livre = shutil.disk_usage(RAIZ).free / 1e9
    if livre < 1:
        sys.exit(f"disco com {livre:.1f} GB livres — liberar espaço antes (cada vídeo ocupa até ~50 MB enquanto é processado)")
    saida = os.path.join(WORK, usuario, "folhas")
    os.makedirs(saida, exist_ok=True)
    reels = sorted(json.load(open(os.path.join(base, "reels.json"), encoding="utf-8")), key=lambda x: -(x["views"] or 0))
    for x in reels[:a.top]:
        sc = x["shortCode"]
        video = os.path.join(saida, f"{sc}.mp4")
        try:
            subprocess.run(["yt-dlp", "--no-warnings", "-q", "-f", "mp4/b", "-o", video, x["url"]], check=True)
            dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", video],
                                       capture_output=True, text=True).stdout)
            passo = max(dur / 16, 1)
            # sem drawtext: a build do ffmpeg desta máquina quebra no fontconfig — o tempo é o passo × posição
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-vf", f"fps=1/{passo:.3f},scale=240:-1,tile=8x2",
                            "-frames:v", "1", os.path.join(saida, f"folha-{sc}.png")], check=True)
            print(f"{sc}: {x['views']} views · {dur:.0f}s · 1 quadro a cada {passo:.1f}s")
        finally:
            if os.path.exists(video):
                os.remove(video)
    print(f"folhas em {saida}")


if __name__ == "__main__":
    main()
