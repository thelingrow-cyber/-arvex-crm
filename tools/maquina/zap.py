"""Máquina de conteúdo: fala com o Vitor no WhatsApp, pela instância `maquina-vitor` da Evolution.

A instância é o número pessoal dele, fora do CRM (sem webhook). A máquina escreve na conversa "Você"
e lê o que ele responde ali. A resposta dele chega com remoteJid em `@lid`, não no JID do número,
por isso a leitura aceita os dois e separa o que é dele do que a máquina mandou pela origem (`source`).
Chave e servidor vêm das variáveis de usuário EVOLUTION_API_URL e EVOLUTION_API_KEY (nunca no código).

uso:  python tools/maquina/zap.py texto "mensagem"
      python tools/maquina/zap.py video <arquivo.mp4> "legenda"
      python tools/maquina/zap.py esperar [minutos]      # imprime a próxima resposta dele
"""
import base64, json, os, subprocess, sys, threading, time, urllib.request

INST = "maquina-vitor"


def _env(nome):
    # o valor gravado no Windows vem primeiro: um terminal aberto antes do setx carrega o valor velho no ambiente
    v = subprocess.run(["powershell", "-NoProfile", "-c", f"[Environment]::GetEnvironmentVariable('{nome}','User')"],
                       capture_output=True, text=True).stdout.strip() or os.environ.get(nome)
    if not v:
        sys.exit(f"falta a variável de usuário {nome}")
    return v


BASE, CHAVE = _env("EVOLUTION_API_URL").rstrip("/"), _env("EVOLUTION_API_KEY")


def _api(caminho, corpo=None, timeout=60):
    req = urllib.request.Request(f"{BASE}{caminho}", headers={"apikey": CHAVE, "Content-Type": "application/json"},
                                 data=json.dumps(corpo).encode() if corpo is not None else None,
                                 method="POST" if corpo is not None else "GET")
    return json.load(urllib.request.urlopen(req, timeout=timeout))


def meu_numero():
    return str(_api(f"/instance/fetchInstances?instanceName={INST}")[0]["ownerJid"]).split("@")[0].split(":")[0]


def texto(msg, citando=None):
    """Manda texto. `citando` = id de uma mensagem da conversa: a resposta sai em cima dela (o Vitor vê a qual se refere)."""
    corpo = {"number": meu_numero(), "text": msg}
    if citando:
        try:
            return _api(f"/message/sendText/{INST}", {**corpo, "quoted": {"key": {"id": citando}}})
        except Exception:                                                  # citação recusada: manda solta
            pass
    return _api(f"/message/sendText/{INST}", corpo)


# ---------- o que a máquina mandou (para ligar a resposta dele ao roteiro ou vídeo certo) ----------
ESTADO = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".estado.json")   # local, fora do git


def estado():
    try:
        return json.load(open(ESTADO, encoding="utf-8"))
    except (OSError, ValueError):
        return {"itens": {}, "visto": 0}


def salvar(e):
    tmp = ESTADO + ".tmp"
    json.dump(e, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, ESTADO)


_trava = threading.RLock()                                              # o maestro grava de várias threads


def registrar(msg_id, item):
    """Guarda o que foi mandado com aquele id: {"tipo": "roteiro"|"video", "codigo": "R3", "pasta": ..., ...}."""
    with _trava:
        e = estado()
        e["itens"][msg_id] = {**item, "enviado": int(time.time())}
        salvar(e)


def guardar(chave, valor):
    with _trava:
        e = estado()
        e[chave] = valor
        salvar(e)


def atualizar(msg_id, **campos):
    with _trava:
        e = estado()
        e["itens"].setdefault(msg_id, {}).update(campos)
        salvar(e)


def _texto_de(msg):
    return (msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text")
            or next((v["caption"] for v in msg.values() if isinstance(v, dict) and v.get("caption")), None))


def _citada(m):
    """Id da mensagem em cima da qual ele respondeu (Responder no WhatsApp), se respondeu em cima de alguma."""
    for c in [m.get("contextInfo")] + [v.get("contextInfo") for v in m.get("message", {}).values() if isinstance(v, dict)]:
        if c and c.get("stanzaId"):
            return c["stanzaId"]
    return None


def novas(desde):
    """Mensagens que o Vitor digitou (ou gravou em áudio) na conversa "Você" depois de `desde`, da mais antiga à mais nova.
    Cada uma: {"id", "ts", "texto" (ou None), "audio": bool, "citada": id ou None}."""
    minhas, vistas, out = conversa_voce(), set(), []
    for j in minhas:
        for m in _api(f"/chat/findMessages/{INST}", {"where": {"key": {"remoteJid": j}}, "page": 1, "offset": 30},
                      timeout=45)["messages"]["records"]:
            k, msg = m.get("key", {}), m.get("message", {}) or {}
            if (not k.get("fromMe") or m.get("source") == "web" or m.get("messageTimestamp", 0) <= desde
                    or k.get("id") in vistas):
                continue
            vistas.add(k["id"])
            out.append({"id": k["id"], "ts": m["messageTimestamp"], "texto": _texto_de(msg),
                        "audio": "audioMessage" in msg, "citada": _citada(m)})
    return sorted(out, key=lambda x: x["ts"])


def transcrever_audio(msg_id):
    """Baixa o áudio que ele mandou e transcreve no Groq (whisper-large-v3). Chave: variável de usuário GROQ_API_KEY."""
    b64 = _api(f"/chat/getBase64FromMediaMessage/{INST}", {"message": {"key": {"id": msg_id}}, "convertToMp4": False},
               timeout=120)["base64"]
    limite = "----maquina" + str(int(time.time()))
    corpo = (f"--{limite}\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\nwhisper-large-v3\r\n"
             f"--{limite}\r\nContent-Disposition: form-data; name=\"language\"\r\n\r\npt\r\n"
             f"--{limite}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"audio.ogg\"\r\n"
             f"Content-Type: audio/ogg\r\n\r\n").encode() + base64.b64decode(b64) + f"\r\n--{limite}--\r\n".encode()
    req = urllib.request.Request("https://api.groq.com/openai/v1/audio/transcriptions", data=corpo, method="POST",
                                 headers={"Authorization": f"Bearer {_env('GROQ_API_KEY')}", "User-Agent": "curl/8.4.0",
                                          "Content-Type": f"multipart/form-data; boundary={limite}"})
    return json.load(urllib.request.urlopen(req, timeout=120))["text"].strip()


def previa(arquivo):
    """Cópia leve (720p) só para aprovar no celular. Mandar 35–55 MB em base64 travou a Evolution inteira
    em 16/10, inclusive a instância do CRM (respostas de 30–60 s). O arquivo cheio vai para o Drive."""
    if os.path.getsize(arquivo) <= 12 * 2**20:
        return arquivo
    leve = os.path.splitext(arquivo)[0] + "-previa.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", arquivo, "-vf", "scale=720:-2", "-c:v", "libx264", "-crf", "28",
                    "-preset", "fast", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart", leve], check=True)
    return leve


def video(arquivo, legenda=""):
    arquivo = previa(arquivo)
    return _api(f"/message/sendMedia/{INST}", {
        "number": meu_numero(), "mediatype": "video", "mimetype": "video/mp4",
        "fileName": os.path.basename(arquivo), "caption": legenda,
        "media": base64.b64encode(open(arquivo, "rb").read()).decode()}, timeout=300)


LID = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".zap-lid")   # local, fora do git


def conversa_voce():
    """JIDs da conversa "Você": o do número e o @lid (as respostas dele chegam no @lid, 16/10).
    O @lid é aprendido uma vez, da 1ª resposta dele ("Vamos com tudo", 16/10), e guardado em .zap-lid."""
    jids = {f"{meu_numero()}@s.whatsapp.net"}
    if not os.path.exists(LID):
        r = _api(f"/chat/findMessages/{INST}", {"where": {"key": {"fromMe": True}}, "page": 1, "offset": 1000}, timeout=60)
        lid = next((m["key"]["remoteJid"] for m in r["messages"]["records"]
                    if "Vamos com tudo" in (m.get("message", {}).get("conversation") or "")), None)
        if lid:
            open(LID, "w").write(lid)
    if os.path.exists(LID):
        jids.add(open(LID).read().strip())
    return jids


def esperar(minutos=30, desde=None):
    """Devolve o texto da próxima mensagem que o Vitor digitar no celular depois de `desde`, ou None."""
    desde = desde or time.time()
    fim = time.time() + minutos * 60
    minhas = conversa_voce()   # só a conversa "Você": mensagem dele para outra pessoa nunca é resposta
    while time.time() < fim:
        try:
            recs = [m for j in minhas for m in _api(f"/chat/findMessages/{INST}", {"where": {"key": {"remoteJid": j}}, "page": 1,
                                                                                  "offset": 20}, timeout=30)["messages"]["records"]]
            for m in recs:
                k = m.get("key", {})
                jid = str(k.get("remoteJid", ""))
                if (not k.get("fromMe") or m.get("source") == "web"          # web = enviada pela máquina
                        or m.get("messageTimestamp", 0) < desde or jid not in minhas):
                    continue
                msg = m.get("message", {})
                t = msg.get("conversation") or msg.get("extendedTextMessage", {}).get("text")
                if t:
                    return t
        except Exception as e:                                             # rede instável não derruba a espera
            print(f"  (falha ao consultar: {e})", file=sys.stderr)
        time.sleep(15)
    return None


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    if a[0] == "texto":
        print(texto(a[1]).get("status"))
    elif a[0] == "video":
        print(video(a[1], a[2] if len(a) > 2 else "").get("status"))
    elif a[0] == "esperar":
        r = esperar(float(a[1]) if len(a) > 1 else 30)
        print(f"RESPOSTA: {r}" if r else "SEM RESPOSTA")
    else:
        sys.exit(__doc__)
