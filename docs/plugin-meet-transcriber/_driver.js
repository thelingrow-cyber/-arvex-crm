/* Driver de teste do parser (não faz parte da extensão). Roda vários cenários. */
(function () {
  var region = document.getElementById("region");
  var P = window.ArvexCaptionParser;
  if (!P) { document.title = "ERR_NO_PARSER"; return; }

  function runScenario(label, ariaLabel, frames) {
    region.setAttribute("aria-label", ariaLabel);
    var transcript = [], active = new Map();
    function lastFor(s){ for (var i=transcript.length-1;i>=0;i--) if (transcript[i].speaker===s) return transcript[i]; return null; }
    function commit(s,t){ var p=lastFor(s); if(p&&p.text===t) return; if(p&&t.indexOf(p.text)===0){p.text=t;return;} transcript.push({speaker:s,text:t}); }
    function tick(){
      var rows=P.parseRows(P.findRegion()), seen={};
      for (var i=0;i<rows.length;i++){ var r=rows[i], k=r.speaker||"_"; seen[k]=1; var a=active.get(k);
        if (a&&a.text===r.text){ a.stable++; if(a.stable>=2){ commit(k==="_"?"":k,r.text); active.delete(k);} }
        else active.set(k,{text:r.text,stable:0}); }
      active.forEach(function(a,k){ if(!seen[k]){ commit(k==="_"?"":k,a.text); active.delete(k);} });
    }
    for (var i=0;i<frames.length;i++){ region.innerHTML=frames[i]; tick(); }
    active.forEach(function(a,k){ commit(k==="_"?"":k,a.text); });
    return label + ": [" + transcript.map(function(t){ return (t.speaker?t.speaker+"|":"")+t.text; }).join(" /// ") + "]";
  }

  // helpers de linha
  function rowImg(sp,tx){ return '<div><img alt="'+sp+'"><div>'+sp+'</div><div>'+tx+'</div></div>'; }     // com avatar
  function rowNoImg(sp,tx){ return '<div><div>'+sp+'</div><div>'+tx+'</div></div>'; }                      // sem avatar (fallback)

  var results = [];

  // Cenário A: 2 falantes com avatar, rolante + sobreposto (PT)
  results.push(runScenario("A_2falantes", "Legendas", [
    rowImg("João","Oi"), rowImg("João","Oi, tudo bem?"), rowImg("João","Oi, tudo bem? Como vai?"), rowImg("João","Oi, tudo bem? Como vai?"),
    rowImg("João","Oi, tudo bem? Como vai?")+rowImg("Maria","Tô"), rowImg("João","Oi, tudo bem? Como vai?")+rowImg("Maria","Tô precisando vender mais"),
    rowImg("Maria","Tô precisando vender mais"), rowImg("Maria","Tô precisando vender mais"),
  ]));

  // Cenário B: 3 falantes (EN aria-label "Captions")
  results.push(runScenario("B_3falantes_EN", "Captions", [
    rowImg("Ana","Hello"), rowImg("Ana","Hello everyone"), rowImg("Ana","Hello everyone"),
    rowImg("Bob","Hi"), rowImg("Bob","Hi Ana"), rowImg("Bob","Hi Ana"),
    rowImg("Carla","Oi gente"), rowImg("Carla","Oi gente"),
  ]));

  // Cenário C: linha SEM avatar (testa fallback :scope>div + extração por prefixo)
  results.push(runScenario("C_sem_avatar", "Legendas", [
    rowNoImg("Pedro","Bom dia"), rowNoImg("Pedro","Bom dia a todos"), rowNoImg("Pedro","Bom dia a todos"),
    rowNoImg("Sofia","Bom dia Pedro"), rowNoImg("Sofia","Bom dia Pedro"),
  ]));

  document.title = "###" + results.join("  ||  ");
})();
