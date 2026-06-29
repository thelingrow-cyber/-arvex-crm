/* Driver de teste do parser (não faz parte da extensão). Espelha o dedupe do content.js. */
(function () {
  var region = document.getElementById("region");
  var P = window.ArvexCaptionParser;
  if (!P) { document.title = "ERR_NO_PARSER"; return; }
  var transcript = [], active = new Map();
  function lastFor(s){ for (var i=transcript.length-1;i>=0;i--) if (transcript[i].speaker===s) return transcript[i]; return null; }
  function commit(s,t){ var p=lastFor(s); if(p&&p.text===t) return; if(p&&t.indexOf(p.text)===0){p.text=t;return;} transcript.push({speaker:s,text:t}); }
  function tick(){
    var rows=P.parseRows(region), seen={};
    for (var i=0;i<rows.length;i++){ var r=rows[i], k=r.speaker||"_"; seen[k]=1; var a=active.get(k);
      if (a&&a.text===r.text){ a.stable++; if(a.stable>=2){ commit(k==="_"?"":k,r.text); active.delete(k);} }
      else active.set(k,{text:r.text,stable:0}); }
    active.forEach(function(a,k){ if(!seen[k]){ commit(k==="_"?"":k,a.text); active.delete(k);} });
  }
  function row(sp,tx){ return '<div><img alt="'+sp+'"><div>'+sp+'</div><div>'+tx+'</div></div>'; }
  var J="João Silva", M="Maria Souza", Jf="Oi, tudo bem? Como vai a ótica?", Mf="Tô precisando vender mais e não sei como";
  var frames=[ row(J,"Oi"), row(J,"Oi, tudo bem?"), row(J,Jf), row(J,Jf),
    row(J,Jf)+row(M,"Tô"), row(J,Jf)+row(M,"Tô precisando vender mais"), row(J,Jf)+row(M,Mf),
    row(M,Mf), row(M,Mf) ];
  for (var i=0;i<frames.length;i++){ region.innerHTML=frames[i]; tick(); }
  active.forEach(function(a,k){ commit(k==="_"?"":k,a.text); });
  document.title = "###" + transcript.map(function(t){ return (t.speaker?t.speaker+": ":"")+t.text; }).join(" || ");
})();
