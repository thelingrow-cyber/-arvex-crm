"""Máquina de conteúdo: fala com o Vitor no WhatsApp, pela instância `maquina-vitor` da Evolution.

A instância é o número pessoal dele, fora do CRM (sem webhook). A máquina escreve na conversa "Você"
e lê o que ele responde ali. A resposta dele chega com remoteJid em `@lid`, não no JID do número,
por isso a leitura aceita os dois e separa o que é dele do que a máquina mandou pela origem (`source`).
Chave e servidor vêm das variáveis de usuário EVOLUTION_API_URL e EVOLUTION_API_KEY (nunca no código).

uso:  python tools/maquina/zap.py texto "mensagem"
      python tools/maquina/zap.py video <arquivo.mp4> "legenda"
      python tools/maquina/zap.py esperar [minutos]      # imprime a próxima resposta dele
"""
import base64, json, os, subprocess, sys, time, urllib.request

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


def texto(msg):
    return _api(f"/message/sendText/{INST}", {"number": meu_numero(), "text": msg})


def video(arquivo, legenda=""):
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
