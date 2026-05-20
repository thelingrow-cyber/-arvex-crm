# Identidade do Produto — Pulso
> Data: 2026-05-19

---

## Nome

**PULSO**

### Por que Pulso
- Proposta central: "sua ótica crescendo mesmo quando você não está" — o sistema está *vivo*, *batendo*, *presente* enquanto o dono dorme
- Duas sílabas — fácil de falar, fácil de lembrar
- Funciona para outros nichos depois sem parecer óptico no branding
- "Pulso CRM", "Pulso IA", "@meupulso" — tudo flui
- O último estágio do pipeline é "Pós-venda Ativo" — o produto mantém o cliente com pulso

### Tagline
> "Seu negócio com pulso. Sempre."

### Nomes descartados e por quê
| Nome | Problema |
|------|----------|
| Tração | Substantivo genérico, soa como nome de curso |
| Impulso | Idem |
| Fluxo | Idem |
| Foco | Muito comum como marca, genérico |
| Velo | Marca de ciclismo — conflito INPI |
| Nexo | Conflito com Nexo Jornal |
| Ativo | Palavra muito comum em finanças |

---

## Identidade Visual

### Paleta

| Token | Hex | Uso |
|-------|-----|-----|
| Primária | `#4F46E5` | Índigo — tech, IA, premium, confiança |
| Accent | `#F59E0B` | Âmbar — energia, luz, foco (remete à lente) |
| Texto | `#0F172A` | Quase preto — leitura limpa |
| Fundo | `#FAFAFA` | Branco quente — leveza |

### Por que NÃO verde
- O white label (Victor Eder) é verde
- Datacrazy é verde
- Chatclipy é verde
- Todo concorrente é verde — porque todo mundo vende "WhatsApp"
- Pulso não vende WhatsApp. Vende crescimento de ótica via IA
- Índigo = linguagem visual de IA (OpenAI, Linear, Notion)
- Âmbar/dourado = luz, lente, foco — contexto óptico sutil sem ser literal

### Logo
- Tipografia: sans-serif bold (Geist, Inter ou similar)
- Sem ícone de óculos — o produto é tech, não óptico no branding visual
- Forma do logo: wordmark "pulso" em lowercase + ponto âmbar como accent (remetendo ao "." de um pulso cardíaco)

### Referências visuais
- Linear (SaaS de gestão): índigo, clean, tipografia bold
- Notion: neutro premium, fundo quase branco
- Contra: sem a complexidade — mais acessível para dono de ótica

---

## Diferenciais do Chat (vs. base white label)

### O que qualquer cliente do Victor Eder tem
- Handoff humano com gatilho configurável
- Ouvir áudio e analisar imagens
- Histórico de conversa (20 msgs)
- Disparos em massa com rotação de número

### O que só o Pulso tem

#### 1. Consulta de OS em tempo real
- Cliente: "meus óculos estão prontos?"
- Agente consulta módulo OS no Supabase via tool calling
- Responde com prazo exato, não resposta genérica
- Nenhum concorrente faz isso

#### 2. Prescrição no contexto da conversa
- O agente sabe a receita do cliente (OD, OE, grau, tipo de lente)
- Usa isso para recomendar produto adequado
- Ex: "Sua receita é de grau alto — recomendo o Varilux X4D para progressiva"

#### 3. Captura de receita por foto
- Cliente envia foto da receita pelo WhatsApp
- Agente lê os dados (Analisar imagens já habilitado)
- Preenche campos de prescrição no CRM automaticamente
- Elimina digitação manual do atendente

#### 4. Campanhas ópticas pré-configuradas
- Ao entrar no Pulso, 3 campanhas já existem prontas:
  1. Prescrição Vencendo (1 ano da última compra)
  2. OS Pronta (óculos chegou do laboratório)
  3. Reativação (6 meses sem contato)
- Dono só precisa ativar — não configura do zero
- Diferencial de onboarding: menos de 1h para disparar a primeira campanha

#### 5. Score de risco de inatividade
- IA calcula: dias sem contato + última compra + ciclo de troca esperado
- Classifica cada cliente: Ativo / Em Risco / Inativo
- Aciona campanha automaticamente quando entra em risco
- Aparece no dashboard como métrica óptica

---

## Análise do White Label (base)

### O que já está pronto (sem código)
| Feature | Status |
|---------|--------|
| Dashboard métricas por período | ✅ |
| CRM multi-board kanban | ✅ |
| Cards com Nome + Produto + Data + Canal | ✅ |
| Pipeline óptico configurável | ✅ (via renomear stages) |
| Agente IA com system prompt | ✅ |
| Handoff humano configurável | ✅ |
| Áudio + imagem no agente | ✅ |
| Disparos em massa multi-conexão | ✅ |
| Rotação de números | ✅ |
| Variáveis de personalização (Nome, Cidade, Empresa) | ✅ |
| Gerador de copy com IA | ✅ |

### O que o Pulso constrói por cima (com código)
| Feature | Prazo |
|---------|-------|
| Campos de prescrição (OD/OE/grau/lente) no card | Semana 2 |
| Módulo OS (número, prazo, status, laboratório) | Semana 2 |
| Consulta de OS via agente (tool calling) | Semana 2 |
| Captura de receita por foto (read + fill CRM) | Semana 3 |
| Score de risco de inatividade | Semana 3 |
| Dashboard métricas ópticas | Semana 4 |
| Campanhas pré-configuradas no onboarding | Semana 2 |

### Observação sobre pipeline óptico
O Base44 já renderizou o pipeline completo com dados fictícios reais:
- Novo Lead → Consulta Agendada → Simulação Realizada → Venda Fechada → OS em Produção → Entregue → Pós-Venda Ativo
- Cards mostram tipo de lente + canal de aquisição — validado visualmente
- Não precisa de código — só configuração do CRM do Victor Eder

---

## Próximos passos imediatos

1. Checar "Pulso" no INPI (registro de marca)
2. Checar domínio: `pulso.ai`, `usepulso.com`, `meupulso.com.br`
3. Criar logo wordmark (Figma ou contratar designer)
4. Configurar white label: renomear pipeline stages + system prompt óptico + campanhas
5. Demo para Cindy com dados fictícios do pipeline óptico
