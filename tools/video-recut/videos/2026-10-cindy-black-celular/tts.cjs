// Gera a narração com o clone profissional da Cindy (ElevenLabs) + tempos por palavra no formato da Groq.
// uso: node tts.cjs   (chave em ELEVENLABS_API_KEY do usuário do Windows)
const fs = require("fs"), path = require("path"), { execSync, execFileSync } = require("child_process");
const NOME = path.basename(__dirname), work = path.join(__dirname, "../../work", NOME);
const VOZ = "plsczSttbqHX09y0ObkG"; // "Cindy Batista PRO" (clone profissional, aprovado 21/10 na comparação D)
const key = process.env.ELEVENLABS_API_KEY || execSync(`powershell -NoProfile -c "[Environment]::GetEnvironmentVariable('ELEVENLABS_API_KEY','User')"`).toString().trim();
const text = fs.readFileSync(path.join(__dirname, "copy.txt"), "utf8").trim();
(async () => {
  const r = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${VOZ}/with-timestamps?output_format=mp3_44100_192`, {
    method: "POST", headers: { "xi-api-key": key, "Content-Type": "application/json" },
    body: JSON.stringify({ text, model_id: "eleven_multilingual_v2", language_code: "pt",
      voice_settings: { stability: 0.32, similarity_boost: 0.85, style: 0.3, use_speaker_boost: true, speed: 1 } }),
  });
  if (!r.ok) throw new Error(r.status + " " + (await r.text()));
  const j = await r.json();
  fs.writeFileSync(path.join(work, "tts.mp3"), Buffer.from(j.audio_base64, "base64"));
  const a = j.normalized_alignment || j.alignment, ch = a.characters, st = a.character_start_times_seconds, en = a.character_end_times_seconds;
  const words = []; let w = null;
  ch.forEach((c, i) => {
    if (/\s/.test(c)) { if (w) words.push(w); w = null; return; }
    if (!w) w = { word: "", start: st[i], end: en[i] };
    w.word += c; w.end = en[i];
  });
  if (w) words.push(w);
  const D = 0.1; // atraso de 100 ms no início
  fs.writeFileSync(path.join(work, "transcricao.json"), JSON.stringify({ words: words.map((x) => ({ ...x, start: x.start + D, end: x.end + D })) }));
  execFileSync("ffmpeg", ["-v", "error", "-y", "-i", path.join(work, "tts.mp3"), "-af", `adelay=100|100,loudnorm=I=-16:TP=-1.5:LRA=11`, "-ar", "48000", "-c:a", "pcm_s16le", path.join(work, "voz.wav")]);
  console.log(words.map((x) => `${x.word}@${(x.start + D).toFixed(2)}`).join(" "));
})().catch((e) => { console.error(e.message); process.exit(1); });
