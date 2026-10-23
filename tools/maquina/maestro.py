"""Maestro da máquina de conteúdo: fica rodando no PC e faz a ponte com o Vitor pelo WhatsApp e pelo Drive.

A cada 30 s lê o que ele escreveu (ou gravou em áudio) na conversa "Você":
  roteiro  · "ok" aprova · "troca" pede outro tema do mesmo molde · qualquer outra coisa é nota: reescreve e manda a v2
  vídeo    · "pode" sobe em Prontos/, agenda no Instagram (Zernio, próximo horário livre) e manda a legenda
             · "cancela" tira da fila · quando o post sai, arquiva sozinho · "postei" arquiva · outra coisa vira ajuste
A resposta é ligada ao item pela mensagem em cima da qual ele respondeu; sem isso, pelo código (R3) no texto;
sem código, pelo único item esperando resposta. Se ficar ambíguo, pergunta.

A cada 2 min olha a raiz da pasta "Vídeos claude" no Drive: vídeo novo é baixado, reconhecido pela fala (qual roteiro é),
cortado (limpar.cjs), planejado (edicao), montado (montar.py) e a prévia vai para o WhatsApp.

Tudo o que ele manda fica em tools/maquina/maestro.log, inclusive o que não é resposta a nada (para o Orion ler na sessão).

uso:  python tools/maquina/maestro.py          # roda para sempre (tarefa "ARVEX Maquina - maestro", ao entrar no Windows)
      python tools/maquina/maestro.py --uma    # uma passada só (teste)
"""
import datetime, difflib, glob, json, os, re, shutil, subprocess, sys, threading, time, traceback, unicodedata

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
import zap        # noqa: E402
import maquina    # noqa: E402
import insta      # noqa: E402

RAIZ = maquina.RAIZ
LOG = os.path.join(AQUI, "maestro.log")
RCLONE = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Rclone.Rclone_Microsoft.Winget.Source_8wekyb3d8bbwe"
                            r"\rclone-v1.75.1-windows-amd64\rclone.exe")
PASTA_DRIVE = "1HbNe1b3WuKUBqaosktWyqtrIW3Loedj1"           # "Vídeos claude" (id, não é segredo)
BAIXADOS = os.path.join(RAIZ, "tools", "video-recut", "videos", "drive")
SIM = {"ok", "okay", "aprovado", "aprovo", "pode", "bora", "show", "top", "fechou", "perfeito", "gostei", "boa", "massa",
       "sim", "isso", "manda", "vai", "otimo", "👍", "✅"}
TROCA = {"troca", "trocar", "outro", "outro tema", "proximo"}
POSTEI = {"postei", "postado", "ja postei", "subi", "publiquei"}
CANCELA = {"cancela", "cancelar", "cancele", "desagenda", "tira da fila", "segura"}
trava = threading.Lock()


def log(txt):
    linha = f"{datetime.datetime.now():%d/%m %H:%M:%S} · {txt}"
    print(linha, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def norm(t):
    t = unicodedata.normalize("NFKD", t.lower()).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", t).split()


MAS = {"mas", "so", "tira", "muda", "mude", "troca", "nao", "menos", "porem", "tirar", "corta"}


def eh(texto, conjunto, max_palavras=4):
    """Resposta curta de uma palavra-chave ("ok", "pode gravar", "já postei"). "ok mas tira X" é nota, não aprovação."""
    p = norm(texto)
    if texto.strip() in conjunto:
        return True
    if not 0 < len(p) <= max_palavras or (conjunto is not TROCA and MAS & set(p)):
        return False
    return " ".join(p) in conjunto or any(w in conjunto for w in p)


def em_segundo_plano(nome, f, *a):
    def corpo():
        try:
            f(*a)
        except Exception as e:
            log(f"ERRO em {nome}: {e}\n{traceback.format_exc()}")
            zap.texto(f"⚠️ Deu erro em {nome}: {str(e)[:300]}\nO Orion vê isso no log.")
    threading.Thread(target=corpo, daemon=True).start()


# ---------- de qual item ele está falando ----------
def alvo(m, itens):
    if m["citada"] in itens:
        return m["citada"]
    cod = re.search(r"\b([RrNn])(\d{1,2})\b", m["texto"] or "")          # R = roteiro da grade, N = notícia da manhã
    hoje = str(datetime.date.today())
    if cod:
        cands = [i for i, v in itens.items() if v.get("codigo") == f"{cod.group(1).upper()}{cod.group(2)}" and v.get("dia") == hoje]
        if cands:
            return max(cands, key=lambda i: itens[i]["enviado"])
    abertos = [i for i, v in itens.items() if v.get("status") in ("enviado", "previa", "agendado") and v.get("dia") == hoje]
    return abertos[0] if len(abertos) == 1 else None


# ---------- roteiro ----------
def mandar_roteiro(item, pasta, cabeca):
    r = zap.texto(f"🎬 *{item['codigo']} · {maquina.ICONE.get(item['molde'], '')} {item['molde']}* · {cabeca}\n\n"
                  + maquina.resumo_zap(os.path.join(RAIZ, pasta)))
    zap.registrar(r["key"]["id"], {**item, "pasta": pasta, "status": "enviado"})


def reescrever(mid, item, nota):
    maquina.reescrever(item["pasta"], nota)
    v = len(glob.glob(os.path.join(RAIZ, item["pasta"], "roteiro-v*.md"))) + 1
    zap.atualizar(mid, status="reescrito")
    mandar_roteiro(item, item["pasta"], f"v{v}, com a sua nota")
    log(f"{item['codigo']} reescrito (v{v})")


def trocar(mid, item):
    livres = [c for c in maquina._temas() if int(c[0]) not in maquina.usados() and c[2] == item["molde"]]
    if not livres:
        maquina.abastecer()
        livres = [c for c in maquina._temas() if int(c[0]) not in maquina.usados() and c[2] == item["molde"]]
    if not livres:
        zap.texto(f"⚠️ Acabaram os temas de {item['molde']}. Me manda um tema ou uma referência.", citando=mid)
        return
    n = int(max(livres, key=lambda c: int(re.sub(r"\D", "", c[5]) or 0))[0])
    r = maquina.roteiro(n)
    zap.atualizar(mid, status="trocado")
    mandar_roteiro({**item, "tema": n}, r.split("→ ")[1].rsplit("/", 1)[0], "tema novo")
    log(f"{item['codigo']} trocado pelo tema {n}")


# ---------- vídeo ----------
def subir_pronto(mid, item):
    pasta = os.path.join(RAIZ, item["pasta"])
    final = os.path.join(pasta, "final.mp4")
    nome = f"{os.path.basename(pasta)[:10]}-{maquina.slug(maquina.resumo_zap(pasta).split(chr(10))[0], 6)}.mp4"
    subprocess.run([RCLONE, "copyto", final, f"drive:Prontos/{nome}", "--drive-root-folder-id", PASTA_DRIVE],
                   check=True, capture_output=True)
    if not os.path.exists(os.path.join(pasta, "legenda.txt")):
        maquina.legenda(pasta)
    leg = open(os.path.join(pasta, "legenda.txt"), encoding="utf-8").read().strip()
    cred = os.path.join(pasta, "CREDITOS.txt")
    cred = open(cred, encoding="utf-8").read().strip() if os.path.exists(cred) else ""
    zap.atualizar(mid, status="aprovado")
    zap.texto(f"✅ {item['codigo']} em *Prontos/{nome}*.\n\nLegenda do post (copia e cola):", citando=mid)
    post = leg + (f"\n\n{cred}" if cred and "nenhum" not in cred.lower() else "")
    zap.texto(post)
    log(f"{item['codigo']} aprovado e no Drive: {nome}")
    # o "pode" é o APROVADO dele: agenda no Instagram no próximo horário livre (12h, 19h ou 21h)
    r = insta.agendar(final, post)
    quando = insta.quando_br(r["quando"])
    zap.atualizar(mid, status="agendado", post_id=r["id"], agendado_para=r["quando"].isoformat(), dia=str(datetime.date.today()))
    aviso = zap.texto(f"📅 {item['codigo']} agendado no Instagram: *{quando}*.\n*cancela* (em cima desta mensagem) = tira da fila. "
                      "Quando sair, eu arquivo e te mando o link.", citando=mid)
    zap.registrar(aviso["key"]["id"], {**item, "tipo": "video", "status": "agendado", "post_id": r["id"],
                                       "agendado_para": r["quando"].isoformat(), "dia": str(datetime.date.today())})
    log(f"{item['codigo']} agendado: {r['id']} · {quando}")


def _mesmo_post(post_id, **campos):
    """O item fica registrado em 2 mensagens (prévia e aviso de agendamento): atualiza as duas."""
    for i, v in zap.estado()["itens"].items():
        if v.get("post_id") == post_id:
            zap.atualizar(i, **campos)


def desagendar(mid, item):
    insta.cancelar(item["post_id"])
    _mesmo_post(item["post_id"], status="previa", post_id=None)
    zap.texto(f"⏸️ {item['codigo']} saiu da fila do Instagram. Responde *pode* na prévia para agendar de novo.", citando=mid)
    log(f"{item['codigo']} desagendado")


def conferir_agendados():
    """Post agendado que já passou do horário: publicado → arquiva e manda o link; falhou → avisa."""
    agora = datetime.datetime.now(insta.FUSO)
    vistos = set()
    for mid, v in list(zap.estado()["itens"].items()):
        pid = v.get("post_id")
        if v.get("status") != "agendado" or not pid or pid in vistos:
            continue
        vistos.add(pid)
        if datetime.datetime.fromisoformat(v["agendado_para"]) > agora:
            continue
        s = insta.situacao(pid)
        if s["status"] == "published":
            _mesmo_post(pid, status="postado")
            maquina.arquivar(v["pasta"])
            zap.texto(f"🟢 {v['codigo']} saiu no Instagram: {s['url'] or '(link ainda não veio)'}\n📦 Arquivado como publicado.")
            log(f"{v['codigo']} publicado: {s['url']}")
        elif s["status"] in ("failed", "partial"):
            _mesmo_post(pid, status="falhou")
            zap.texto(f"🔴 {v['codigo']} NÃO saiu no Instagram: {s['erro'] or s['status']}. O Orion vê na próxima sessão.")
            log(f"{v['codigo']} falhou ao publicar: {s}")


def arquivar(mid, item):
    maquina.arquivar(item["pasta"])
    zap.atualizar(mid, status="postado")
    zap.texto(f"📦 {item['codigo']} arquivado como publicado.", citando=mid)


# ---------- uma mensagem dele ----------
def tratar(m):
    if m["audio"] and not m["texto"]:
        m["texto"] = zap.transcrever_audio(m["id"])
        log(f"áudio transcrito: {m['texto']}")
    texto = (m["texto"] or "").strip()
    itens = zap.estado()["itens"]
    mid = alvo(m, itens)
    log(f"ele: {texto!r} → {itens[mid]['codigo'] + ' ' + itens[mid]['tipo'] if mid else 'sem alvo'}")
    if not texto:
        return
    if not mid:
        abertos = [v["codigo"] for v in itens.values() if v.get("status") in ("enviado", "previa")
                   and v.get("dia") == str(datetime.date.today())]
        if abertos and (eh(texto, SIM | TROCA | POSTEI) or m["citada"]):
            zap.texto(f"Não sei de qual você está falando ({', '.join(abertos)}). Responde *em cima* da mensagem "
                      "ou começa com o código, tipo *R3 ok*.")
        return                                                          # recado solto: fica no log para o Orion
    item = itens[mid]
    resto = re.sub(r"^\s*[RrNn]\d{1,2}\s*[:,.-]?\s*", "", texto)
    eco = f"🎙️ Entendi: _{texto}_\n\n" if m["audio"] else ""
    if item["tipo"] == "roteiro":
        if eh(resto, SIM):
            zap.atualizar(mid, status="aprovado")
            zap.texto(f"{eco}✅ {item['codigo']} aprovado. Grava e sobe no Drive.", citando=mid)
        elif eh(resto, TROCA):
            zap.texto(f"{eco}🔄 {item['codigo']}: buscando outro tema de {item['molde']} (uns minutos).", citando=mid)
            em_segundo_plano(f"troca do {item['codigo']}", trocar, mid, item)
        else:
            zap.texto(f"{eco}📝 {item['codigo']}: reescrevendo com a sua nota (uns minutos).", citando=mid)
            em_segundo_plano(f"reescrita do {item['codigo']}", reescrever, mid, item, resto)
    elif item["tipo"] == "video":
        if item.get("status") == "agendado" and eh(resto, CANCELA):
            em_segundo_plano(f"cancelamento do {item['codigo']}", desagendar, mid, item)
        elif item.get("status") == "agendado" and eh(resto, SIM):
            zap.texto(f"{eco}📅 {item['codigo']} já está na fila do Instagram.", citando=mid)
        elif eh(resto, POSTEI):
            em_segundo_plano(f"arquivo do {item['codigo']}", arquivar, mid, item)
        elif eh(resto, SIM):
            zap.texto(f"{eco}⬆️ {item['codigo']}: subindo em Prontos, escrevendo a legenda e agendando no Instagram.", citando=mid)
            em_segundo_plano(f"aprovação do {item['codigo']}", subir_pronto, mid, item)
        else:
            with open(os.path.join(RAIZ, item["pasta"], "ajustes-do-vitor.md"), "a", encoding="utf-8") as f:
                f.write(f"- {datetime.datetime.now():%d/%m %H:%M} · {resto}\n")
            zap.atualizar(mid, status="ajuste")
            zap.texto(f"{eco}✍️ {item['codigo']}: ajuste anotado. Ajuste de edição eu faço na próxima sessão com o Orion "
                      "e te mando a nova prévia.", citando=mid)


def ler_whatsapp():
    desde = zap.estado().get("visto") or int(time.time()) - 60        # 1ª vez: não reprocessa o histórico
    for m in zap.novas(desde):
        zap.guardar("visto", m["ts"])                                   # antes de tratar: erro não faz responder 2 vezes
        try:
            tratar(m)
        except Exception as ex:
            log(f"ERRO tratando {m}: {ex}\n{traceback.format_exc()}")
    zap.guardar("visto", max(desde, zap.estado().get("visto") or 0))


# ---------- Drive: vídeo novo → qual roteiro → corte → edição → prévia ----------
def drive_lista():
    r = subprocess.run([RCLONE, "lsf", "drive:", "--drive-root-folder-id", PASTA_DRIVE, "--files-only",
                        "--include", "*.{mp4,MP4,mov,MOV,m4v}"], capture_output=True, text=True, encoding="utf-8")
    return [l.strip() for l in r.stdout.splitlines() if l.strip()] if r.returncode == 0 else None


def fala_inicio(video):
    """Transcreve o primeiro minuto (Groq) para descobrir qual roteiro ele gravou."""
    aud = video + ".m4a"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-t", "60", "-vn", "-ac", "1", "-b:a", "64k", aud], check=True)
    import base64, urllib.request
    limite = "----maestro"
    corpo = (f"--{limite}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-large-v3\r\n"
             f"--{limite}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\npt\r\n"
             f"--{limite}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"a.m4a\"\r\n"
             f"Content-Type: audio/mp4\r\n\r\n").encode() + open(aud, "rb").read() + f"\r\n--{limite}--\r\n".encode()
    os.remove(aud)
    req = urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=corpo, method="POST",
                                 headers={"Authorization": f"Bearer {zap._env('GROQ_API_KEY')}", "User-Agent": "curl/8.4.0",
                                          "Content-Type": f"multipart/form-data; boundary={limite}"})
    return json.load(urllib.request.urlopen(req, timeout=180))["text"]


def qual_roteiro(fala):
    """O roteiro enviado (ainda não gravado) cuja fala mais se parece com o começo do vídeo."""
    itens = zap.estado()["itens"]
    cands = {v["pasta"]: (i, v) for i, v in sorted(itens.items(), key=lambda x: x[1]["enviado"])
             if v.get("tipo") == "roteiro" and v.get("status") in ("enviado", "aprovado")}
    alvo_p = " ".join(norm(fala))[:600]
    nota = {p: difflib.SequenceMatcher(None, alvo_p, " ".join(norm(maquina.resumo_zap(os.path.join(RAIZ, p))))[:600]).ratio()
            for p in cands if os.path.isdir(os.path.join(RAIZ, p))}
    if not nota:
        return None, 0
    p = max(nota, key=nota.get)
    return cands[p], nota[p]


def processar_video(nome):
    os.makedirs(BAIXADOS, exist_ok=True)
    local = os.path.join(BAIXADOS, nome)
    subprocess.run([RCLONE, "copyto", f"drive:{nome}", local, "--drive-root-folder-id", PASTA_DRIVE],
                   check=True, capture_output=True)
    fala = fala_inicio(local)
    achado, nota = qual_roteiro(fala)
    if not achado or nota < 0.25:
        log(f"vídeo {nome}: não achei o roteiro (semelhança {nota:.2f}). Fala: {fala[:200]}")
        zap.texto(f"🎥 Chegou *{nome}* no Drive, mas não reconheci de qual roteiro é. Fica para o Orion editar à mão.")
        return
    mid, item = achado
    pasta = os.path.join(RAIZ, item["pasta"])
    os.makedirs(os.path.join(pasta, "bruto"), exist_ok=True)
    shutil.copy(local, os.path.join(pasta, "bruto", nome))
    zap.atualizar(mid, status="gravado")
    zap.texto(f"🎥 Recebi o *{item['codigo']}* ({nome}). Editando, a prévia chega em uns minutos.", citando=mid)
    maquina.corte(item["pasta"])
    maquina.par_voz(item["pasta"])                                      # a máquina aprende com o que ele mudou ao falar
    maquina.edicao(item["pasta"])
    py = sys.executable.replace("pythonw.exe", "python.exe")           # pythonw não tem console: o print do montar.py quebrava (19/10)
    subprocess.run([py, os.path.join(AQUI, "montar.py"), os.path.basename(pasta)], check=True, cwd=RAIZ)
    r = zap.video(os.path.join(pasta, "final.mp4"), f"🎬 {item['codigo']} editado. *pode* = agenda no Instagram · "
                                                     "ou responde em cima com o que ajustar.")
    zap.registrar(r["key"]["id"], {**item, "tipo": "video", "status": "previa", "dia": str(datetime.date.today())})
    log(f"{item['codigo']}: prévia enviada ({nome})")


def ler_drive():
    atuais = drive_lista()
    if atuais is None:
        return
    vistos = zap.estado().get("drive")
    if vistos is None:                                                  # 1ª vez: o que já está lá não é novo
        zap.guardar("drive", atuais)
        return
    novos = [n for n in atuais if n not in vistos]
    if novos:
        zap.guardar("drive", sorted(set(vistos) | set(novos)))
        for n in novos:
            log(f"Drive: vídeo novo {n}")
            em_segundo_plano(f"edição de {n}", com_trava, processar_video, n)


def com_trava(f, *a):
    with trava:                                                         # um vídeo por vez: ffmpeg já usa a máquina toda
        f(*a)


def sem_janela():
    """Rodando por pythonw (tarefa ao entrar no Windows) não há console: print iria para None e cada ffmpeg, rclone ou
    claude abriria uma janela piscando. Manda a saída para o nada e cria os processos filhos sem janela."""
    if sys.stdout is None:
        sys.stdout = sys.stderr = open(os.devnull, "w", encoding="utf-8")
    if os.name == "nt":
        original = subprocess.Popen.__init__

        def init(self, *a, **k):
            k.setdefault("creationflags", 0x08000000)                   # CREATE_NO_WINDOW
            original(self, *a, **k)
        subprocess.Popen.__init__ = init


def main():
    sem_janela()
    sys.stdout.reconfigure(encoding="utf-8")
    uma = "--uma" in sys.argv
    log("maestro ligado")
    n = 0
    while True:
        try:
            ler_whatsapp()
            if n % 4 == 0:
                ler_drive()
                conferir_agendados()
        except Exception as e:                                          # rede caiu: tenta de novo na próxima volta
            log(f"falha na volta: {e}")
        if uma:
            break
        n += 1
        time.sleep(30)


if __name__ == "__main__":
    main()
