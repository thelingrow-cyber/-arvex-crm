"""Clone do Vitor nos grupos de WhatsApp: lê o grupo, decide se responde e responde no jeito dele.

Roda no PC do Vitor, pela instância `maquina-vitor` (o número pessoal dele), e usa o Claude da assinatura dele
(`claude -p`), sem chave de API. O estilo e as regras estão em `perfil-voz-vitor.md`; grupos e limites em `config.json`.

O que o clone faz em cada grupo ligado:
- espera a conversa dar uma pausa e só então decide (ninguém responde no meio de uma rajada);
- fica calado se o próprio Vitor falou no grupo há pouco (mensagem do celular, não da API);
- responde com 1 a 3 mensagens curtas, com "digitando..." e atraso variável;
- quando o assunto é dele de verdade (dinheiro, compromisso, conflito...), não responde: chama o Vitor na conversa "Você".

uso:  python tools/maquina/clone/clone.py            # roda em laço
      python tools/maquina/clone/clone.py --uma-vez  # uma rodada (teste)
"""
import json, os, random, subprocess, sys, tempfile, time

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(AQUI))
import zap  # noqa: E402

CONFIG = os.path.join(AQUI, "config.json")
PERFIL = os.path.join(AQUI, "perfil-voz-vitor.md")
ESTADO = os.path.join(AQUI, ".estado-clone.json")   # local, fora do git
LOG = os.path.join(AQUI, "clone.log")                # local, fora do git
# fora do repositório: assim o `claude -p` não carrega o CLAUDE.md do projeto nem a persona dos agentes
CWD_CLAUDE = os.path.join(tempfile.gettempdir(), "clone-vitor")


def log(txt):
    linha = time.strftime("%d/%m %H:%M:%S ") + txt
    print(linha, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(linha + "\n")


def carregar(caminho, padrao):
    try:
        return json.load(open(caminho, encoding="utf-8"))
    except (OSError, ValueError):
        return padrao


def salvar_estado(e):
    tmp = ESTADO + ".tmp"
    json.dump(e, open(tmp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    os.replace(tmp, ESTADO)


# ---------- leitura do grupo ----------

def mensagens(jid, n=40):
    recs = zap._api(f"/chat/findMessages/{zap.INST}", {"where": {"key": {"remoteJid": jid}}, "page": 1, "offset": n},
                    timeout=60)["messages"]["records"]
    return sorted(recs, key=lambda m: int(m.get("messageTimestamp", 0)))


def do_vitor_no_celular(m):
    """Mensagem que o Vitor digitou de verdade (não a que o clone mandou pela API, que vem com source=web)."""
    return m.get("key", {}).get("fromMe") and m.get("source") != "web"


def texto_da(m, cache):
    msg = m.get("message") or {}
    t = zap._texto_de(msg)
    if t:
        return t
    mid = m.get("key", {}).get("id")
    if "audioMessage" in msg:
        if mid not in cache:
            try:
                cache[mid] = "[áudio] " + zap.transcrever_audio(mid)
            except Exception as e:
                cache[mid] = "[áudio que não deu pra ouvir]"
                log(f"falha ao transcrever {mid}: {e}")
        return cache[mid]
    tipo = (m.get("messageType") or "mídia").replace("Message", "")
    return {"sticker": "[figurinha]", "image": "[foto]", "video": "[vídeo]", "document": "[arquivo]"}.get(tipo, f"[{tipo}]")


_MEUS = None


def marcar_vitor(t):
    """Menção ao Vitor chega como @<número> ou @<lid>; troca por @Vitor para o modelo saber que falaram com ele."""
    global _MEUS
    if _MEUS is None:
        _MEUS = {j.split("@")[0] for j in zap.conversa_voce()}
    for n in _MEUS:
        t = t.replace("@" + n, "@Vitor")
    return t


def transcricao(recs, cache):
    linhas = []
    for m in recs:
        quem = "Vitor" if m.get("key", {}).get("fromMe") else (m.get("pushName") or "alguém")
        hora = time.strftime("%H:%M", time.localtime(int(m.get("messageTimestamp", 0))))
        linhas.append(f"[{hora}] {quem}: {marcar_vitor(texto_da(m, cache))}")
    return "\n".join(linhas)


# ---------- decisão ----------

def decidir(grupo, conversa, cfg):
    perfil = open(PERFIL, encoding="utf-8").read()
    prompt = f"""Você é o clone do Vitor no WhatsApp. Vai ler a conversa de um grupo e decidir o que o Vitor faria agora.
Ninguém pode perceber que não é ele. Siga o perfil abaixo à risca: o tom e o tamanho das mensagens dele são o que mais importa.

{perfil}

Grupo: "{grupo['nome']}" (tom: {grupo['tom']}). Observações deste grupo: {grupo.get('obs', '-')}

Conversa recente (a última linha é a mais nova; "Vitor" é ele):
{conversa}

Decida UMA ação:
- "ignorar": não há gancho pra ele (só áudios/figurinhas entre outros, assunto que ele não acrescenta nada).
- "responder": marcaram ele (@Vitor), falaram com ele, perguntaram algo pra ele, ou a conversa tem um gancho em que ele
  entraria com uma reação ou comentário (siga o quanto ele participa neste grupo, descrito no perfil e nas observações).
- "chamar": o assunto precisa do Vitor de verdade (ver regras do perfil). Não responda nada no grupo nesse caso.

Responda SÓ com um JSON, sem texto em volta:
{{"acao": "ignorar|responder|chamar", "mensagens": ["msg1", "msg2"], "motivo": "uma frase", "sugestao": "o que ele poderia responder (só em chamar)"}}
Em "responder", 1 a {cfg['max_msgs']} mensagens (uma só é o mais comum), curtas como as dele, sem ponto final.
Nunca invente fato, memória, jogo, placar ou história que não esteja na conversa (é o jeito mais fácil de ser pego). Prefira a reação mais curta possível: uma palavra seca vale mais que uma frase. Não repita as palavras de quem falou, não comece sempre com "kkk", não dê bom dia por educação: comente por cima, com opinião."""
    os.makedirs(CWD_CLAUDE, exist_ok=True)
    r = subprocess.run(["claude", "-p", "--model", cfg.get("modelo", "sonnet"), "--max-turns", "1"],
                       input=prompt, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, cwd=CWD_CLAUDE,
                       shell=(os.name == "nt"))
    saida = r.stdout.strip()
    ini, fim = saida.find("{"), saida.rfind("}")
    if ini < 0:
        raise ValueError(f"resposta sem JSON: {saida[:200]} {(r.stderr or "")[:200]}")
    d = json.loads(saida[ini:fim + 1])
    if d.get("acao") not in ("ignorar", "responder", "chamar"):
        raise ValueError(f"ação inválida: {d}")
    d["mensagens"] = [str(x).strip() for x in (d.get("mensagens") or []) if str(x).strip()][:cfg["max_msgs"]]
    return d


# ---------- envio ----------

def enviar_grupo(jid, msgs):
    for i, t in enumerate(msgs):
        # "delay" mostra "digitando..." antes de enviar; proporcional ao tamanho, como uma pessoa
        zap._api(f"/message/sendText/{zap.INST}",
                 {"number": jid, "text": t, "delay": int(min(6000, 900 + 120 * len(t)) * random.uniform(0.8, 1.3))},
                 timeout=60)
        if i < len(msgs) - 1:
            time.sleep(random.uniform(1.5, 5))


def chamar_vitor(grupo, conversa, d):
    ultimas = "\n".join(conversa.splitlines()[-6:])
    zap.texto(f"🤖 *Clone · {grupo['nome']}*: preciso de você\n\n{ultimas}\n\n*Por quê:* {d.get('motivo', '')}\n"
              f"*Sugestão:* {d.get('sugestao', '-')}")


def relatar(grupo, d):
    zap.texto(f"🤖 *Clone · {grupo['nome']}* respondeu:\n" + "\n".join(f"> {m}" for m in d["mensagens"])
              + f"\n_({d.get('motivo', '')})_")


# ---------- rodada ----------

def rodada(cfg, est):
    agora = time.time()
    hora = time.localtime(agora).tm_hour
    ini, fim = cfg["horario"]
    if not (ini <= hora < fim):
        return
    for jid, g in cfg["grupos"].items():
        if g.get("modo") not in ("ativo", "sombra"):
            continue
        ge = est.setdefault(jid, {"visto": 0, "respostas": [], "audios": {}})
        try:
            recs = mensagens(jid)
        except Exception as e:
            log(f"{g['nome']}: falha ao ler ({e})")
            continue
        novas = [m for m in recs if int(m.get("messageTimestamp", 0)) > ge["visto"]
                 and not (m.get("key", {}).get("fromMe") and m.get("source") == "web")]
        if not novas:
            continue
        ultima = int(recs[-1].get("messageTimestamp", 0))
        if agora - ultima < cfg["pausa_s"]:                 # conversa ainda rolando: espera a pausa
            continue
        ge["visto"] = ultima
        if agora - ultima > cfg.get("max_idade_min", 30) * 60:   # conversa velha (ex.: da madrugada): não ressuscita
            continue
        if any(do_vitor_no_celular(m) and agora - int(m["messageTimestamp"]) < cfg["silencio_se_vitor_min"] * 60
               for m in recs):
            log(f"{g['nome']}: Vitor está no grupo, clone quieto")
            continue
        ge["respostas"] = [t for t in ge["respostas"] if agora - t < 3600]
        if len(ge["respostas"]) >= cfg["max_por_hora"]:
            log(f"{g['nome']}: limite de {cfg['max_por_hora']} respostas/hora")
            continue
        conversa = transcricao(recs[-cfg["contexto"]:], ge["audios"])
        try:
            d = decidir(g, conversa, cfg)
        except Exception as e:
            log(f"{g['nome']}: falha na decisão ({e})")
            continue
        log(f"{g['nome']}: {d['acao']} · {d.get('motivo', '')} · {d.get('mensagens')}")
        if d["acao"] == "chamar":
            chamar_vitor(g, conversa, d)
        elif d["acao"] == "responder" and d["mensagens"]:
            if g["modo"] == "sombra":                        # sombra: só mostra ao Vitor o que teria mandado
                zap.texto(f"🤖 *Clone (sombra) · {g['nome']}* teria respondido:\n"
                          + "\n".join(f"> {m}" for m in d["mensagens"]) + f"\n_({d.get('motivo', '')})_")
                continue
            time.sleep(random.uniform(*cfg["atraso_s"]))
            depois = mensagens(jid, 15)                     # o Vitor pode ter aparecido enquanto o clone "pensava"
            if any(do_vitor_no_celular(m) and int(m["messageTimestamp"]) > ultima for m in depois):
                log(f"{g['nome']}: Vitor apareceu, resposta descartada")
                continue
            enviar_grupo(jid, d["mensagens"])
            ge["respostas"].append(time.time())
            if cfg.get("relatar_respostas"):
                relatar(g, d)
        ge["audios"] = dict(list(ge["audios"].items())[-200:])


def main():
    uma = "--uma-vez" in sys.argv
    est = carregar(ESTADO, {})
    cfg = carregar(CONFIG, None)
    if not cfg:
        sys.exit("falta config.json")
    if not est:                                              # 1ª vez: não responde ao histórico, só ao que vier depois
        for jid in cfg["grupos"]:
            est[jid] = {"visto": int(time.time()), "respostas": [], "audios": {}}
        salvar_estado(est)
        log("estado criado: o clone só reage a mensagens novas a partir de agora")
    log("clone ligado: " + ", ".join(f"{g['nome']} ({g['modo']})" for g in cfg["grupos"].values()))
    while True:
        cfg = carregar(CONFIG, cfg)                          # dá pra mudar o config.json com o clone rodando
        try:
            rodada(cfg, est)
        except Exception as e:
            log(f"erro na rodada: {e}")
        salvar_estado(est)
        if uma:
            break
        time.sleep(cfg["intervalo_s"])


if __name__ == "__main__":
    main()
