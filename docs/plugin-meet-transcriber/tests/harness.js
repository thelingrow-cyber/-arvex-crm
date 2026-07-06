/* Harness de teste (não faz parte da extensão).
 * Roda o parser REAL (caption-parser.js) + o core REAL (transcript-core.js)
 * contra um DOM mutado incrementalmente (como o Meet faz de verdade — atualiza
 * texto de nós existentes — não substitui o container inteiro a cada frame,
 * que é o que o driver antigo fazia e por isso não testava o pipeline real). */
window.__runFixture = function (frames, checkFn) {
  var region = document.getElementById("region");
  var P = window.ArvexCaptionParser;
  var C = window.ArvexTranscriptCore;
  if (!P || !C) {
    document.getElementById("result").textContent = JSON.stringify({ name: "harness", pass: false, error: "parser ou core não carregou" });
    document.title = "FAIL";
    return;
  }
  var store = C.createStore();
  var clock = 1000000; // relógio fake determinístico (nada de Date.now em teste)
  function now() { return clock; }
  function tick() {
    var rows = [];
    try { rows = P.parseRows(P.findRegion()); } catch (e) {}
    for (var i = 0; i < rows.length; i++) store.upsert(rows[i], { now: now });
  }
  for (var f = 0; f < frames.length; f++) {
    frames[f](region);
    clock += 700; // avança como um tick real de 700ms
    tick();
  }
  var transcript = store.transcript.map(function (r) { return { speaker: r.speaker, text: r.text }; });
  var out = checkFn(transcript);
  document.getElementById("result").textContent = JSON.stringify(out);
  document.title = out.pass ? "PASS" : "FAIL";
};
