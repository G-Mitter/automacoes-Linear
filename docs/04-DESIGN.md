# Briefing de Design — Automações Linear

- **Versão:** 1.1
- **Data:** 2026-11-10
- **Status:** aprovado
- **Base:** PRD v1.0, Fluxo v1.0

---

Na V1 o "visual" se resume a três coisas: o **terminal**, as **mensagens do Telegram** e os **nomes de arquivos e pastas**. A parte de cores e componentes já fica definida para a futura interface (RF-16), para que ela nasça com um padrão.

**Regra:** todo componente novo deve seguir este documento.

## 1. Estilo e sensação
**Operacional, claro, confiável, discreto, direto.** É uma ferramenta de trabalho: o status precisa ser entendido em 2 segundos, sem enfeites.

## 2. Paleta de cores
| Uso | Hex | Onde |
|---|---|---|
| Primária | `#C8102E` | Vermelho do SGLinear (marca do ERP); botões principais e destaques |
| Secundária | `#1F2937` | Cabeçalhos, barra lateral |
| Fundo | `#F7F7F8` (claro) / `#111318` (escuro) | Fundo das telas |
| Superfície | `#FFFFFF` / `#1A1D24` | Cartões e tabelas |
| Texto | `#111827` / `#E5E7EB` | Texto principal |
| Texto secundário | `#6B7280` / `#9CA3AF` | Rótulos e datas |
| Sucesso | `#15803D` | Status OK |
| Erro | `#B91C1C` | Status FALHA |
| Aviso | `#B45309` | SEM DADOS, retentativa, aguardando servidor |
| Informação | `#1D4ED8` | Em andamento |

**Regra:** o status **nunca** é indicado só pela cor. Sempre há texto ou ícone junto (✅ OK, ❌ FALHA, ⚠️ SEM DADOS, ⏳ EM ANDAMENTO).

## 3. Terminal (V1)
**Cores:** usar as cores do terminal correspondentes à paleta, pela biblioteca `rich` (adicionada ao TRD na E1).

| Elemento | Formato |
|---|---|
| Cabeçalho | `Curva ABC · modo individual · 22 filiais · execução 2026-11-10_1432` |
| Progresso | barra + `F06 (3/22) · tentativa 1/3 · exportando…` |
| Linha de evento | `14:33:02  ✅ F04  CurvaABC_2026-11-10_F04.xlsx` |
| Erro | `14:35:40  ❌ F06  mensagem vermelha (exportação) → nova tentativa 2/3` |
| Resumo final | tabela com as colunas Filial · Status · Tentativas · Arquivo/Erro |

## 4. Telegram (V1)
- Primeira linha com um ícone de status e o nome do processo, para ser legível na notificação do celular.
- No máximo 6 linhas. Os detalhes ficam no log.
- O comando para refazer as falhas vai dentro de um bloco de código, para copiar com um toque.

## 5. Nomes de arquivos e pastas
- **Processo:** em PascalCase (palavras juntas, cada uma com maiúscula), sem acento nem espaço. Exemplo: `CurvaABC`, `ProdutosInativos`.
- **Arquivo:** `<Processo>_<AAAA-MM-DD>[_F<NN>].<ext>`. A filial tem no mínimo 2 dígitos, então a filial 3 fica `F03` e a 76 fica `F76`.
- **Pasta:** `<pasta base>\<Processo>\`.

## 6. Tipografia (interface futura)
| Uso | Fonte | Tamanho | Peso |
|---|---|---|---|
| Título de página | Inter | 24px | 600 |
| Título de seção/cartão | Inter | 18px | 600 |
| Corpo | Inter | 14px | 400 |
| Rótulo/legenda | Inter | 12px | 500 |
| Números, logs, nomes de arquivo | JetBrains Mono | 13px | 400 |

## 7. Espaçamento, bordas, sombras, ícones (interface futura)
- **Espaçamento:** escala de 4px (4, 8, 12, 16, 24, 32).
- **Bordas:** raio de 8px em cartões e campos, 6px em botões; linha de 1px `#E5E7EB` (no tema escuro, `#2A2F3A`).
- **Sombra:** só em modais (`0 8px 24px rgba(0,0,0,.12)`).
- **Ícones:** Lucide, tamanho 16 ou 20px.

## 8. Componentes padrão (interface futura)
| Componente | Normal | Hover | Desabilitado | Erro |
|---|---|---|---|---|
| Botão primário ("Rodar") | fundo primária, texto branco | escurece 10% | 40% de opacidade, sem clique | — |
| Botão secundário | borda + texto secundária | fundo cinza claro | 40% de opacidade | — |
| Seleção de filiais | grade de caixas (22) + "Todas"/"Nenhuma" | borda primária | cinza (filial inativa) | contorno vermelho se nenhuma marcada |
| Campo | borda cinza | borda mais escura | fundo cinza | borda e mensagem em vermelho |
| Cartão de automação | superfície + borda | borda primária | — | faixa vermelha à esquerda se a última execução teve falha |
| Tabela de execução | linhas alternadas | linha destacada | — | linha com etiqueta ❌ |
| Etiqueta de status | texto + ícone + fundo claro da cor do status | — | — | — |
| Modal | centralizado, sombra | — | — | — |
| Mensagem (aviso) | barra no topo com ícone | — | — | — |

## 9b. Widget flutuante (interface futura, anotado em 2026-11-13)
Ideia do usuário para a futura interface visual (RF-16), registrada aqui para não se perder até a etapa de construí-la:
- Uma **bolinha flutuante** fica sobre as outras janelas, sempre visível, no **canto superior direito** da tela enquanto alguma automação está em execução.
- A bolinha muda de cor conforme o status (ex.: azul rodando, vermelha com falha), parecido com a etiqueta de status (§8).
- **Clicar na bolinha abre um painel** com:
  - a lista de automações disponíveis, para escolher e iniciar outras automações por ali (não só pela linha de comando);
  - os detalhes da execução atual (filial, etapa, progresso);
  - a **lista de erros que apareceram** na execução (tipo, filial, hora, print) — por isso a E6 já grava cada erro de forma estruturada no `ItemExecucao.erros` (Backend §1.6), pronta para essa lista ser só uma leitura do JSON.
- Essa UI fica fora do escopo da V1 (que é linha de comando + Telegram), mas o registro estruturado dos erros já é construído agora para não exigir retrabalho depois.

## 9. Responsividade e acessibilidade
- A interface futura será usada principalmente no PC. Ela deve funcionar a partir de 1280px de largura e ser legível no celular, já que o uso pelo celular é desejado.
- O contraste do texto deve ser de no mínimo 4,5:1 (padrão WCAG AA).
- Áreas de clique de no mínimo 40px de altura. No celular, 44px.
- Toda ação também deve funcionar pelo teclado (Tab e Enter).

---

## Histórico de mudanças
| Versão | Data | Mudança |
|---|---|---|
| 1.1 | 2026-11-13 | Anotada a ideia do widget flutuante (bolinha) para a interface futura, com painel de automações e lista de erros |
| 0.1 | 2026-11-10 | Primeiro rascunho |
| 1.0 | 2026-11-10 | Aprovado |
