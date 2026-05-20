# Prompt — Demo SaaS Óptico (Base44)

Cole esse prompt no Base44 para gerar a versão de demonstração:

---

Crie uma aplicação web de demonstração de um SaaS para negócios do nicho óptico (óticas). O sistema é uma plataforma de crescimento com IA que atende, qualifica e retém clientes automaticamente via WhatsApp.

## Objetivo da demo
Mostrar para donos de ótica como o sistema funciona na prática, com dados fictícios já preenchidos para simular uma ótica real em operação.

## Telas que devem existir

### 1. Dashboard principal
- Métricas em destaque: Novos leads hoje, Atendimentos realizados pela IA, Clientes em risco de inatividade, Faturamento estimado gerado
- Gráfico de leads por semana (últimas 4 semanas)
- Lista dos últimos 5 atendimentos da IA com status (resolvido / encaminhado para humano)
- Alerta visual: "3 clientes com prescrição vencida há mais de 30 dias"

### 2. Funil de clientes
- Kanban com etapas: Novo Lead → Consulta Agendada → Simulação Realizada → Venda Fechada → OS em Produção → Entregue → Pós-venda Ativo
- Cards de clientes fictícios em cada etapa (usar nomes brasileiros)
- Cada card mostra: nome, tipo de lente de interesse, origem (WhatsApp, Instagram, indicação), data de entrada

### 3. Atendimentos da IA
- Lista de conversas recentes simuladas entre a IA e clientes
- Cada conversa deve mostrar: pergunta do cliente → resposta da IA
- Exemplos de conversas:
  - Cliente perguntando preço de lente progressiva → IA responde com faixa de preço e agenda consulta
  - Cliente perguntando status dos óculos → IA responde com status da OS
  - Cliente novo sem prescrição → IA orienta a agendar consulta e coleta nome/telefone
- Badge indicando se foi resolvido pela IA ou transferido para humano

### 4. Retenção de clientes
- Lista de clientes com score de risco (verde / amarelo / vermelho)
- Critérios visíveis: dias desde última compra, status da prescrição, histórico de ajustes
- Botão "Enviar campanha de reativação" (ação simulada)
- Clientes em vermelho com sugestão automática: "Prescrição vence em 15 dias — sugerimos enviar mensagem de renovação"

### 5. Configurações básicas (simplificado)
- Nome da ótica
- Número do WhatsApp conectado
- Horário de atendimento da IA
- Mensagem de boas-vindas personalizada

## Dados fictícios para usar
- Nome da ótica demo: **Ótica Visão Clara**
- Cidade: São Paulo - SP
- Leads novos hoje: 7
- Atendimentos IA (últimas 24h): 23
- Clientes em risco: 4
- Conversão do mês: 34%

## Visual e estilo
- Interface limpa, moderna, cores neutras com destaque em azul ou verde
- Linguagem simples — o usuário é dono de ótica, não técnico
- Ícones claros, sem jargão técnico
- Mobile-friendly (donos de ótica acessam pelo celular)

## Comportamento da demo
- Todos os botões de ação mostram uma mensagem de sucesso simulada
- Nenhuma integração real necessária — tudo é mockado
- Incluir botão "Quero esse sistema para minha ótica" em destaque no topo, que abre um formulário simples (nome, WhatsApp, cidade)
