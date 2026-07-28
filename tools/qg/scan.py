"""
QG — varredura do repositório ARVEX.

Extrai o estado real dos squads, agentes e clones direto dos arquivos-fonte.
Nada aqui é digitado à mão: se o repo mudar, a varredura muda junto.

Uso:  python tools/qg/scan.py            # imprime o resumo
      python tools/qg/scan.py --json     # despeja o estado em JSON
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SQUADS = ROOT / "squads"
CLONES = ROOT / ".claude" / "clones"
CORE_AGENTS = ROOT / ".aiox-core" / "development" / "agents"


# ── helpers de parsing ────────────────────────────────────────────────
def scalar(text: str, key: str, *, block: str | None = None) -> str | None:
    """Lê `key: valor` — opcionalmente só dentro de um bloco `block:`."""
    scope = text
    if block:
        m = re.search(rf"^{block}:\s*$(.*?)(?=^\S|\Z)", text, re.M | re.S)
        if not m:
            return None
        scope = m.group(1)
    m = re.search(rf"^\s*{key}:\s*[\"']?(.+?)[\"']?\s*$", scope, re.M)
    return m.group(1).strip() if m else None


def listing(text: str, key: str) -> list[str]:
    """Lê uma lista YAML simples `key:\\n  - a\\n  - b`."""
    m = re.search(rf"^{key}:\s*$((?:\s*-\s*.+\n?)+)", text, re.M)
    if not m:
        return []
    out = []
    for line in m.group(1).splitlines():
        item = line.strip()
        if not item.startswith("-"):
            continue
        item = item[1:].strip().strip("\"'")
        item = item.split("#")[0].strip()  # tira comentário inline
        if item:
            out.append(item)
    return out


def yaml_block(md: str) -> str:
    """Devolve o primeiro bloco ```yaml ...``` de um arquivo de agente."""
    m = re.search(r"```yaml\s*(.*?)```", md, re.S)
    return m.group(1) if m else md


# ── coletores ─────────────────────────────────────────────────────────
def read_squads() -> list[dict]:
    squads = []
    for manifest in sorted(SQUADS.glob("*/squad.yaml")):
        raw = manifest.read_text(encoding="utf-8", errors="replace")
        sd = manifest.parent
        squad = {
            "id": scalar(raw, "name") or sd.name,
            "title": scalar(raw, "title") or sd.name,
            "description": scalar(raw, "description") or "",
            "icon": scalar(raw, "icon") or "",
            "namespace": scalar(raw, "namespace") or "",
            "created_at": scalar(raw, "created_at") or "",
            "tasks_declared": int(scalar(raw, "tasks_count") or 0),
            "workflow_steps": int(scalar(raw, "workflow_steps") or 0),
            "agents": [],
        }
        for af in sorted((sd / "agents").glob("*.md")):
            squad["agents"].append(read_agent(af, squad["id"]))
        squad["agents"].sort(key=lambda a: (not a["is_lead"], a["persona"]))
        squads.append(squad)
    return squads


def read_agent(path: Path, squad_id: str) -> dict:
    raw = path.read_text(encoding="utf-8", errors="replace")
    y = yaml_block(raw)
    sources = [s for s in listing(y, "knowledge_sources")]

    # ligações declaradas no campo estruturado
    formal = {
        re.sub(r"^\.claude/clones/|/$", "", s)
        for s in sources
        if "clones/" in s
    }
    # ligações citadas em qualquer lugar do arquivo (inclusive prosa)
    mentioned = set(re.findall(r"\.claude/clones/([a-z0-9\-]+)", raw))
    clones = sorted(formal | mentioned)
    # material documental da casa que o agente cita — clone não é a única fonte
    docs = sorted(set(re.findall(r"(?:docs|\.aiox-core)/[A-Za-z0-9_.\-/]+", raw))
                  - {s for s in sources if "clones/" in s})
    # comandos e tasks declarados
    cmds = len(re.findall(r"^\s*-\s*name:\s*", y, re.M))
    tasks = len(listing(y, "tasks"))
    return {
        "id": scalar(y, "id", block="agent") or path.stem,
        "squad": squad_id,
        "persona": scalar(y, "name", block="persona") or path.stem,
        "role": scalar(y, "role", block="persona") or "",
        "icon": scalar(y, "icon", block="agent") or "",
        "is_lead": (scalar(y, "is_lead", block="agent") or "").lower() == "true",
        "sources": sources,
        "docs": docs,
        "clones": clones,
        "clones_formal": sorted(formal),
        "clones_prose_only": sorted(mentioned - formal),
        "commands": cmds,
        "tasks": tasks or cmds,
        "file": str(path.relative_to(ROOT)).replace("\\", "/"),
    }


def read_clones() -> list[dict]:
    out = []
    if not CLONES.exists():
        return out
    for cd in sorted(p for p in CLONES.iterdir() if p.is_dir()):
        core = ["system.md", "beliefs.md", "heuristics.md", "context.md"]
        present = [f for f in core if (cd / f).exists()]

        # Profundidade = fato de sistema de arquivos, não texto:
        # material-fonte ingerido de verdade (transcrição/PDF destilado) vs só lista de links.
        research = ROOT / "docs" / f"clone-{cd.name}-pesquisa"
        ingested = len(list(research.rglob("*"))) if research.exists() else 0
        srcdir = cd / "sources"
        distilled = [
            p for p in srcdir.glob("*.md") if p.name != "index.md"
        ] if srcdir.exists() else []
        depth = "primária" if (ingested or distilled) else "consultiva"

        out.append({
            "id": cd.name,
            "files": len(present),
            "complete": len(present) == 4,
            "depth": depth,
            "source_docs": ingested + len(distilled),
            "has_command": (ROOT / ".claude" / "commands" / "AIOX" / "clone" / f"{cd.name}.md").exists(),
        })
    return out


def read_core_agents() -> list[str]:
    if not CORE_AGENTS.exists():
        return []
    return sorted(p.stem for p in CORE_AGENTS.glob("*.md") if not p.stem.startswith("."))


def git(*args: str) -> str:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=20,
        ).stdout.strip()
    except Exception:
        return ""


def read_activity(limit: int = 12) -> list[dict]:
    raw = git("log", f"-{limit}", "--date=short", "--format=%h\x1f%ad\x1f%s")
    rows = []
    for line in raw.splitlines():
        parts = line.split("\x1f")
        if len(parts) == 3:
            rows.append({"sha": parts[0], "date": parts[1], "subject": parts[2]})
    return rows


def read_pending() -> dict:
    """Estado operacional que não dá para derivar — mantido à mão, pequeno."""
    f = ROOT / "docs" / "qg" / "estado.yaml"
    if not f.exists():
        return {"blocks": [], "findings": [], "last_op": None}
    raw = f.read_text(encoding="utf-8", errors="replace")

    def section(name: str) -> list[dict]:
        m = re.search(rf"^{name}:\s*$(.*?)(?=^\w|\Z)", raw, re.M | re.S)
        if not m:
            return []
        items = []
        for chunk in re.split(r"^\s*-\s+", m.group(1), flags=re.M)[1:]:
            d = {}
            for ln in chunk.splitlines():
                kv = re.match(r"\s*(\w+):\s*[\"']?(.*?)[\"']?\s*$", ln)
                if kv:
                    d[kv.group(1)] = kv.group(2)
            if d:
                items.append(d)
        return items

    return {
        "blocks": section("bloqueios"),
        "findings": section("achados"),
        "last_op": scalar(raw, "ultima_operacao"),
    }


def build_state() -> dict:
    squads = read_squads()
    clones = read_clones()
    agents = [a for s in squads for a in s["agents"]]
    fed = {c for a in agents for c in a["clones"]}
    return {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "head": git("rev-parse", "--short", "HEAD"),
        "squads": squads,
        "clones": clones,
        "core_agents": read_core_agents(),
        "activity": read_activity(),
        "state": read_pending(),
        "totals": {
            "squads": len(squads),
            "agents": len(agents),
            "clones": len(clones),
            "links": sum(len(a["clones"]) for a in agents),
            "orphan_clones": [c["id"] for c in clones if c["id"] not in fed],
            "consultive_clones": sum(1 for c in clones if c["depth"] == "consultiva"),
            # fonte é qualquer material real: clone OU documento da casa
            "agents_with_sources": sum(1 for a in agents if a["clones"] or a["docs"]),
            "agents_without_clone": sum(1 for a in agents if not a["clones"]),
            "prose_only_links": sum(len(a["clones_prose_only"]) for a in agents),
        },
    }


if __name__ == "__main__":
    # console Windows (cp1252) não engole → nem ·; força UTF-8 na saída
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    st = build_state()
    if "--json" in sys.argv:
        print(json.dumps(st, ensure_ascii=False, indent=2))
    else:
        t = st["totals"]
        print(f"QG · {st['branch']}@{st['head']} · {st['generated_at']}")
        print(f"  squads {t['squads']} · agentes {t['agents']} · clones {t['clones']}")
        print(f"  ligações clone→agente: {t['links']}  (agentes com fonte: {t['agents_with_sources']})")
        print(f"  clones órfãos: {t['orphan_clones'] or 'nenhum'}")
        print(f"  clones em profundidade consultiva: {t['consultive_clones']}/{t['clones']}")
        print(f"  ligações só em prosa (não estruturadas): {t['prose_only_links']}")
        print()
        for s in st["squads"]:
            lead = next((a["persona"] for a in s["agents"] if a["is_lead"]), "—")
            print(f"  {s['icon']} {s['id']:<11} {len(s['agents']):>2} agentes · lead {lead}")
