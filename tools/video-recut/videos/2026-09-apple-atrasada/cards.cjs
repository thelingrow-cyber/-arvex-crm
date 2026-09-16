// Gera os ASS dos dois cards de texto (660x440)
const fs = require('fs');
const head = (bg) => [
  '[Script Info]', 'ScriptType: v4.00+', 'PlayResX: 660', 'PlayResY: 440', 'WrapStyle: 2', '',
  '[V4+ Styles]',
  'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
  'Style: K,Segoe UI,26,&H0066A2C5,&H0066A2C5,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,0,0,7,0,0,0,1',
  'Style: T,Segoe UI,46,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1',
  'Style: S,Segoe UI,24,&H00B4B4B4,&H00B4B4B4,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,1,0,0,0,1',
  'Style: G,Segoe UI,84,&H0066A2C5,&H0066A2C5,&H00000000,&H00000000,-1,0,0,0,100,100,1,0,1,0,0,5,0,0,0,1',
  '', '[Events]', 'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text', ''].join('\n');
const ev = (st, x, y, txt) => `Dialogue: 0,0:00:00.00,0:00:10.00,${st},,0,0,0,,{\\pos(${x},${y})}${txt}\n`;

fs.writeFileSync(__dirname + '/card-quebra.ass', head() +
  ev('K', 44, 50, 'ABRIL DE 2019') +
  ev('T', 44, 110, 'Samsung adia o lançamento\\Ndo Galaxy Fold depois que\\Na tela quebrou nas mãos\\Nde jornalistas') +
  ev('S', 44, 400, 'Fonte: Bloomberg, 22/04/2019'));

fs.writeFileSync(__dirname + '/card-imposto.ass', head() +
  ev('G', 330, 220, 'IMPOSTO DA\\NDESCOBERTA'));
console.log('ok');
