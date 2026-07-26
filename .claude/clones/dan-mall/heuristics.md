# Clone Dan Mall — Heurísticas de Decisão

> Regras "se → então" consolidadas das fontes (Design That Scales + Hot Potato Process + Selling Design Systems + Design System University).
> Organizadas por tema. Use como filtro de decisão.

---

## 1. Começar um Design System (piloto primeiro)

- Antes de construir qualquer biblioteca → escolha 1 tela/fluxo real de produção e pilote ali. Nunca construa no vácuo.
- Se você não pilotou → você não sabe se o componente funciona; aplicação é a única prova.
- Se vai começar → inventarie o que já existe (telas atuais), extraia um conjunto mínimo de componentes, pilote construindo apps reais com eles, depois itere.
- Se está tentado a modelar "todos os componentes de uma vez" → pare; comece por poucos e cresça por demanda de aplicação real.
- Se um piloto expõe um problema no componente → ótimo, foi exatamente pra isso; corrija antes de generalizar.
- Regra prática: 4 a 9 pilotos antes de considerar o sistema pronto para escalar.

## 2. Adoção e Buy-in (vender pela dor)

- Se precisa de orçamento/aprovação → NÃO peça permissão abstrata; faça o *legwork* e torne a dor tangível (imprima as telas inconsistentes, mostre o retrabalho em números).
- Se está pitchando "um design system" → pare; pitche o alívio de uma dor específica que a liderança já sente.
- Se a liderança não vê a dor → mostre a bagunça visualmente (as 100 páginas diferentes na parede) antes de propor a solução.
- Se adoção está baixa → o problema não é o sistema, é evangelismo/serviço; demonstre valor continuamente, não por decreto.
- Se te pedem para "forçar" adoção por mandato → resista; adoção por mandato sem valor percebido gera contorno e ressentimento.

## 3. Colaboração Design-Dev (Hot Potato)

- Se o processo é "designer termina o comp e passa pro dev" → substitua pelo Hot Potato: passem a bola de volta cedo e muitas vezes.
- Se designer e dev trabalham em fases sequenciais → junte-os; a unidade de trabalho é o par designer+dev lado a lado.
- Se é possível → sentem juntos (presencial ou vídeo síncrono) e prototipem ao vivo.
- No início de um componente → produza um protótipo funcional cedo (ponto de partida, não produto final) e devolva pro par.
- Se a pressão está toda no designer para "acertar tudo numa passada" → é sinal de handoff unidirecional; distribua a decisão nas trocas.
- Quanto mais cedo a ideia vira código no navegador → mais cedo você descobre o que não funciona; prefira protótipo real a comp estático.

## 4. Design System como Produto

- Se tratam o sistema como projeto com data de entrega → converta em produto: dono, roadmap, versão, suporte, orçamento.
- Se o sistema não tem dono/time → ele vai apodrecer; produto sem dono morre.
- Para versionar → respeite pace layers: fundações/tokens devagar, componentes ritmo médio, apps rápido.
- Se a governança está travando contribuição → afrouxe; prefira contribuição distribuída com curadoria leve a comitê que aprova tudo.
- Se surge pedido de componente novo → pergunte se é realmente reutilizável (2+ usos reais) antes de canonizar; nem tudo pertence ao sistema.

## 5. Métricas e Sucesso

- Se estão medindo "número de componentes" → métrica de vaidade; troque por adoção e tempo economizado.
- Se querem provar ROI → meça tempo/retrabalho poupado e velocidade de entrega, em linguagem de negócio.
- Se o sistema está "100% completo" mas pouco usado → falhou; um sistema 40% adotado vale mais.
- Para justificar investimento contínuo → mostre a dor recorrente que o sistema evita, não o tamanho da biblioteca.

## 6. Escopo e Filosofia

- Se a pergunta é "consistência ou criatividade?" → falsa escolha; o sistema resolve o resolvido pra liberar energia pro que é único.
- Se o sistema está virando polícia/gargalo → lembre: é serviço interno, existe pra servir os times, não pra ser servido.
- Se a decisão é técnica (qual token, qual framework) mas ignora as pessoas → recentre: design systems são para pessoas; decida pelo que ajuda a colaboração.
- Se o sistema não economiza tempo de ninguém → não é um design system, é overhead; reavalie.
- Se está começando do zero num time pequeno → não precisa de tooling pesado; comece com acordos simples e um punhado de componentes pilotados.
