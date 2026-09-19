"""Recorte de pessoa quadro a quadro -> vídeo de máscara (branco = pessoa).

Modelo: torchvision deeplabv3_mobilenet_v3_large (classe VOC 15 = pessoa), pesos oficiais do PyTorch.
O RobustVideoMatting via torch.hub recorta melhor o cabelo, mas executa código baixado do GitHub e é
bloqueado pelo classificador de segurança — por isso este.

Custo real (notebook 6 GB RAM, 4 threads): ~1 quadro/s em 540x960. Recorte SÓ o trecho que precisa.
uso: python recorte.py <video> <saida.mp4> <inicio_s> <duracao_s>
"""
import subprocess, sys, time
import numpy as np, torch
from torchvision.models.segmentation import deeplabv3_mobilenet_v3_large, DeepLabV3_MobileNet_V3_Large_Weights

W, H = 540, 960
MEAN = torch.tensor([0.485, 0.456, 0.406])[:, None, None]
STD = torch.tensor([0.229, 0.224, 0.225])[:, None, None]


def recortar(src, dst, inicio, duracao):
    torch.set_num_threads(4)
    seg = deeplabv3_mobilenet_v3_large(weights=DeepLabV3_MobileNet_V3_Large_Weights.DEFAULT).eval()
    leitor = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", str(inicio), "-t", str(duracao), "-i", src,
                               "-vf", f"fps=30,scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                              stdout=subprocess.PIPE)
    escritor = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "gray",
                                 "-s", f"{W}x{H}", "-r", "30", "-i", "-", "-c:v", "libx264", "-crf", "12",
                                 "-pix_fmt", "yuv420p", "-g", "30", dst], stdin=subprocess.PIPE)
    ema, n, t0 = None, 0, time.time()
    with torch.no_grad():
        while True:
            buf = leitor.stdout.read(W * H * 3)
            if len(buf) < W * H * 3:
                break
            x = torch.from_numpy(np.frombuffer(buf, np.uint8).reshape(H, W, 3).copy()).permute(2, 0, 1).float() / 255
            p = seg(((x - MEAN) / STD)[None])["out"].softmax(1)[:, 15:16]
            ema = p if ema is None else 0.6 * p + 0.4 * ema   # suaviza no tempo: a borda não pisca
            escritor.stdin.write((ema[0, 0].clamp(0, 1) * 255).byte().numpy().tobytes())
            n += 1
            if n % 150 == 0:
                print(f"  recorte: {n} quadros ({n / (time.time() - t0):.1f} q/s)", flush=True)
    escritor.stdin.close(); escritor.wait(); leitor.kill()
    print(f"  recorte ok: {n} quadros em {time.time() - t0:.0f}s")


if __name__ == "__main__":
    recortar(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]))
