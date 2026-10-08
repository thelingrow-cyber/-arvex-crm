"""Faixa presidencial no take real (0 → FIM s), sem IA paga.

Pipeline por quadro (1080x1920):
  1. MediaPipe Pose  → ombro direito dele (lm 12, lado esquerdo da tela) e quadril esquerdo (lm 23).
  2. Faixa = tira de tecido (verde | amarelo | verde, bordas douradas) dobrada numa curva que segue o peito.
  3. Luz: a faixa herda a luminância da camisa (dobras e a sombra diagonal) → não parece adesivo.
  4. Recorte: só dentro do corpo (MediaPipe Selfie Segmentation); mãos, microfone e antebraços
     (MediaPipe Hands + segmento cotovelo→punho) ficam NA FRENTE da faixa.
  5. Sombra suave da faixa na camisa.
Landmarks e máscaras suavizados no tempo (sem tremor).

uso: python faixa.py [FIM_s]   → work/2026-10-presidente-ia/faixa.mp4 + faixa-contato.jpg
"""
import os, subprocess, sys
sys.path.insert(0, "C:/Users/Public/mpenv")   # mediapipe quebra com acento no caminho do usuario
import numpy as np, cv2, mediapipe as mp

AQUI = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.dirname(os.path.dirname(AQUI)), "work", "2026-10-presidente-ia")
ORIG = os.path.join(os.path.expandvars(r"%USERPROFILE%"), "Downloads", "FE55C986-B422-4E8F-86E1-7ACC24B82C9F.mp4")
FIM = float(sys.argv[1]) if len(sys.argv) > 1 else 5.2
W, H, FPS = 1080, 1920, 30
DW, DH = 540, 960            # resolução da detecção


# ---------- textura da faixa (comprimento x largura) ----------
def textura(L=2400, Wd=320):
    x = np.linspace(0, 1, Wd)[None, :].repeat(L, 0)
    verde = np.array([6, 112, 62], np.float32)        # verde-bandeira (menos saturado)
    amarelo = np.array([242, 198, 34], np.float32)    # amarelo-ouro
    ouro = np.array([212, 175, 55], np.float32)
    img = np.zeros((L, Wd, 3), np.float32)
    img[:] = verde
    img[(x > 0.36) & (x < 0.64)] = amarelo
    borda = (x < 0.035) | (x > 0.965)
    img[borda] = ouro
    filete = ((x > 0.345) & (x < 0.36)) | ((x > 0.64) & (x < 0.655))
    img[filete] = ouro * 0.95
    # brilho de cetim: faixa clara em diagonal ao longo do comprimento + leve queda nas bordas
    y = np.linspace(0, 1, L)[:, None].repeat(Wd, 1)
    brilho = 1 + 0.10 * np.cos((x * 2.2 + y * 0.6) * np.pi) ** 8
    borda_sombra = 0.80 + 0.20 * np.sin(np.clip(x, 0, 1) * np.pi) ** 0.6   # tecido curvado sobre o peito
    img *= (brilho * borda_sombra)[..., None]
    return np.clip(img, 0, 255)


TEX = textura()


def bezier(p0, p1, p2, t):
    t = t[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t ** 2 * p2


def desenhar(A, B, largura, curva):
    """Projeta TEX na curva A→B. Devolve (rgb float HxWx3, alfa float HxW)."""
    n = 220
    t = np.linspace(0, 1, n)
    d = B - A
    normal = np.array([-d[1], d[0]]) / (np.linalg.norm(d) + 1e-6)
    ctrl = (A + B) / 2 + normal * curva
    c = bezier(A, ctrl, B, t)
    tang = np.gradient(c, axis=0)
    tang /= np.linalg.norm(tang, axis=1, keepdims=True) + 1e-6
    nrm = np.stack([-tang[:, 1], tang[:, 0]], 1)
    # largura afina um pouco no ombro (perspectiva: o tecido vira por cima do ombro)
    wv = largura * (0.82 + 0.18 * np.clip(t * 3, 0, 1))[:, None]
    esq, dir_ = c - nrm * wv / 2, c + nrm * wv / 2
    Lt, Wt = TEX.shape[:2]
    rgb = np.zeros((H, W, 3), np.float32)
    alfa = np.zeros((H, W), np.float32)
    for i in range(n - 1):
        src = np.float32([[0, Lt * t[i]], [Wt - 1, Lt * t[i]], [Wt - 1, Lt * t[i + 1]], [0, Lt * t[i + 1]]])
        dst = np.float32([esq[i], dir_[i], dir_[i + 1], esq[i + 1]])
        y0, y1 = int(max(0, dst[:, 1].min() - 2)), int(min(H, dst[:, 1].max() + 3))
        x0, x1 = int(max(0, dst[:, 0].min() - 2)), int(min(W, dst[:, 0].max() + 3))
        if y1 <= y0 or x1 <= x0:
            continue
        sy0, sy1 = int(Lt * t[i]), int(min(Lt, Lt * t[i + 1] + 2))
        pedaco = TEX[sy0:sy1]
        src[:, 1] -= sy0
        dst_l = dst - [x0, y0]
        M = cv2.getPerspectiveTransform(src, dst_l.astype(np.float32))
        w_rgb = cv2.warpPerspective(pedaco, M, (x1 - x0, y1 - y0), flags=cv2.INTER_LINEAR,
                                    borderMode=cv2.BORDER_REPLICATE)   # sem isso a emenda puxa preto = 'escada'
        m = np.zeros((y1 - y0, x1 - x0), np.uint8)
        cv2.fillConvexPoly(m, np.round(dst_l).astype(np.int32), 255, lineType=cv2.LINE_8)
        m = cv2.dilate(m, np.ones((3, 3), np.uint8))
        mf = m.astype(np.float32) / 255
        sel = mf > 0
        rgb[y0:y1, x0:x1][sel] = w_rgb[sel]
        alfa[y0:y1, x0:x1] = np.maximum(alfa[y0:y1, x0:x1], mf)
    alfa = cv2.GaussianBlur(alfa, (0, 0), 0.9)   # borda macia só no contorno externo
    return rgb, alfa


def suavizar(arr, k=9):
    """Média móvel centrada por coluna (landmarks no tempo)."""
    arr = np.asarray(arr, np.float64)
    pad = np.pad(arr, ((k // 2, k // 2), (0, 0)), mode="edge")
    ker = np.ones(k) / k
    return np.stack([np.convolve(pad[:, j], ker, mode="valid") for j in range(arr.shape[1])], 1)


def ler_quadros():
    p = subprocess.Popen(["ffmpeg", "-v", "error", "-t", str(FIM), "-i", ORIG, "-vf", f"fps={FPS},scale={W}:{H}",
                          "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    while True:
        b = p.stdout.read(W * H * 3)
        if len(b) < W * H * 3:
            break
        yield np.frombuffer(b, np.uint8).reshape(H, W, 3)


def main():
    os.makedirs(WORK, exist_ok=True)
    pose = mp.solutions.pose.Pose(model_complexity=2, smooth_landmarks=True, enable_segmentation=True)
    maos = mp.solutions.hands.Hands(max_num_hands=2, model_complexity=1, min_detection_confidence=0.4)

    # passada 1: detectar
    dados = []
    for f in ler_quadros():
        pq = cv2.resize(f, (DW, DH), interpolation=cv2.INTER_AREA)
        r = pose.process(pq)
        lm = r.pose_landmarks.landmark if r.pose_landmarks else None
        pts = np.array([[lm[i].x * W, lm[i].y * H] for i in (0, 11, 12, 13, 14, 15, 16, 23, 24)]) if lm else None
        seg = cv2.resize(r.segmentation_mask, (W, H)) if r.segmentation_mask is not None else None
        rh = maos.process(pq)
        hs = [np.array([[p.x * W, p.y * H] for p in h.landmark]) for h in (rh.multi_hand_landmarks or [])]
        dados.append((pts, seg, hs))
    print(f"detectados {len(dados)} quadros", flush=True)

    # preencher falhas e suavizar landmarks
    pts = [d[0] for d in dados]
    ult = next(p for p in pts if p is not None)
    for i, p in enumerate(pts):
        if p is None:
            pts[i] = ult
        ult = pts[i]
    P = suavizar(np.array([p.reshape(-1) for p in pts]), 11).reshape(len(pts), -1, 2)

    esc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-crf", "14", "-preset", "slow",
                            "-pix_fmt", "yuv420p", "-g", "30", os.path.join(WORK, "faixa.mp4")], stdin=subprocess.PIPE)
    seg_ema, oc_ema = None, None
    folha = []
    for i, f in enumerate(ler_quadros()):
        if i >= len(dados):
            break
        _, seg, hs = dados[i]
        nariz, ombE, ombD, cotE, cotD, punE, punD, quaE, quaD = P[i]   # E = esquerdo DELE (lado direito da tela)
        larg_omb = np.linalg.norm(ombE - ombD)
        cima = np.array([0, -1.0])
        # A: em cima do ombro direito dele, puxado um pouco pro pescoço; continua por trás do ombro
        A = ombD + 0.22 * (ombE - ombD) + cima * 0.08 * larg_omb
        # câmera baixa e perto: o quadril fica fora do quadro; a faixa sai pelo canto inferior oposto (~43°)
        B = np.array([ombE[0] + 0.05 * larg_omb, ombD[1] + 0.95 * larg_omb])
        dirAB = (B - A) / np.linalg.norm(B - A)
        A_ext = A - dirAB * 0.35 * larg_omb
        B_ext = B + dirAB * 0.6 * larg_omb
        largura = 0.30 * larg_omb
        rgb, alfa = desenhar(A_ext, B_ext, largura, curva=-0.06 * larg_omb)

        img = f.astype(np.float32)
        # 3. luz da camisa
        lum = cv2.GaussianBlur(cv2.cvtColor(f, cv2.COLOR_RGB2GRAY).astype(np.float32), (0, 0), 6)
        ref = np.median(lum[alfa > 0.5]) if (alfa > 0.5).any() else 200
        sombra = np.clip(lum / max(ref, 1), 0.45, 1.12) ** 0.9
        rgb *= sombra[..., None]
        rgb = cv2.GaussianBlur(rgb, (0, 0), 1.1)
        rgb += np.random.default_rng(i).normal(0, 3.2, rgb.shape).astype(np.float32)

        # 4. corpo e oclusão
        corpo = seg if seg is not None else np.ones((H, W), np.float32)
        seg_ema = corpo if seg_ema is None else 0.55 * corpo + 0.45 * seg_ema
        corpo_m = cv2.GaussianBlur(np.clip((seg_ema - 0.35) / 0.3, 0, 1), (0, 0), 2)
        oc = np.zeros((H, W), np.uint8)
        for h in hs:
            hull = cv2.convexHull(h.astype(np.int32))
            cv2.fillConvexPoly(oc, hull, 255)
            for a_, b_ in mp.solutions.hands.HAND_CONNECTIONS:
                cv2.line(oc, tuple(h[a_].astype(int)), tuple(h[b_].astype(int)), 255, 34)
        larg_braco = int(0.17 * larg_omb)
        for c_, p_ in ((cotE, punE), (cotD, punD)):
            cv2.line(oc, tuple(c_.astype(int)), tuple(p_.astype(int)), 255, larg_braco)
        # cabeça e pescoço nunca recebem faixa
        cab = np.zeros((H, W), np.uint8)
        cv2.ellipse(cab, (int(nariz[0]), int(nariz[1] + 0.06 * larg_omb)), (int(0.30 * larg_omb), int(0.26 * larg_omb)), 0, 0, 360, 255, -1)
        oc = cv2.dilate(oc, np.ones((9, 9), np.uint8))
        oc = (np.maximum(oc, cab)).astype(np.float32) / 255
        oc_ema = oc if oc_ema is None else np.maximum(oc, 0.35 * oc_ema)
        oc_m = cv2.GaussianBlur(oc_ema, (0, 0), 3)
        a = alfa * corpo_m * (1 - oc_m)

        # 5. sombra da faixa na camisa (desloca pra baixo/direita, borrada)
        som = cv2.GaussianBlur(np.roll(np.roll(a, 7, 0), 5, 1), (0, 0), 7)
        img *= (1 - 0.22 * som * (1 - a))[..., None]
        out = img * (1 - a[..., None]) + rgb * a[..., None]
        out = np.clip(out, 0, 255).astype(np.uint8)
        esc.stdin.write(out.tobytes())
        if i % 20 == 0:
            folha.append(cv2.resize(out, (270, 480)))
    esc.stdin.close(); esc.wait()
    linhas = [np.hstack(folha[k:k + 4] + [np.zeros_like(folha[0])] * (4 - len(folha[k:k + 4]))) for k in range(0, len(folha), 4)]
    cv2.imwrite(os.path.join(WORK, "faixa-contato.jpg"), cv2.cvtColor(np.vstack(linhas), cv2.COLOR_RGB2BGR))
    print("ok: faixa.mp4 + faixa-contato.jpg", flush=True)


if __name__ == "__main__":
    main()
