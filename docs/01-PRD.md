# PRD — Automações Linear (SGLinear)

- **Versão:** 1.1
- **Data:** 2026-11-10
- **Status:** rascunho (mudança de escopo aguardando aprovação)

---

## 1. Visão geral
Plataforma de automações (RPA, ou seja, um "robô" que usa mouse e teclado como uma pessoa) para o ERP SGLinear, acessado por Terminal Server dentro do Chrome. O primeiro módulo tira relatórios do ERP, exporta em PDF ou Excel, traz o arquivo do servidor para o PC local e o organiza em pastas com nome padronizado. O projeto vai crescer aos poucos, com novos módulos e rotinas.

## 2. Problema e público-alvo
- **Problema:** gerar relatórios no SGLinear é manual e repetitivo. São muitos cliques, os filtros mudam e às vezes é preciso um arquivo por filial (22 filiais). Além disso, o ERP tem erros intermitentes. Isso consome tempo e gera falhas humanas.
- **Público:** o responsável de TI/operação (usuário único na V1), que dispara as automações no próprio PC.
- **Restrição técnica central:** o ERP roda no servidor e chega ao PC só como **imagem** (Terminal Server no Chrome). Não há botões nem campos que o robô possa ler diretamente, então ele precisa reconhecer imagens e textos na tela.

## 3. Objetivos e como medir sucesso
| Objetivo | Medida de sucesso na V1 |
|---|---|
| Automatizar o relatório de Curva ABC | Rodar de ponta a ponta sem intervenção para as filiais escolhidas |
| Organizar os arquivos | 100% dos arquivos salvos na pasta e com o nome padrão |
| Resistir aos erros do ERP | Erros conhecidos tratados sozinhos; a execução nunca para por erro em uma filial |
| Dar visibilidade | Toda falha registrada em log, avisada no Telegram e visível no resumo da execução |
| Facilitar novos relatórios | Uma variação de filtro vira um novo **perfil** sem escrever código |

## 4. Funcionalidades da V1

| ID | Funcionalidade | Prioridade |
|---|---|---|
| RF-01 | Executar uma **rotina** de relatório a partir da tela inicial do SGLinear já logado | Essencial |
| RF-02 | Abrir a tela do relatório e selecionar o **modelo de filtro salvo** no ERP (botão "Filtros" → lista "Filtro de Relatórios"). Os filtros fixos ficam no modelo; **período e filiais são preenchidos pelo robô** | Essencial |
| RF-03 | Selecionar filiais (números, **grupos** ou todas), marcadas pelo próprio robô na lista do "+" do campo Filial. Três modos: **individual** (um arquivo por filial), **por grupo** (um arquivo por grupo) ou **consolidado** (tudo num arquivo) | Essencial |
| RF-04 | Exportar o relatório em **PDF, Excel ou os dois**, escolhido a cada execução (o perfil traz um padrão), salvando no servidor | Essencial |
| RF-05 | Transferir o arquivo do servidor para o PC pela janela "Descarregar arquivo" e localizar o download | Essencial |
| RF-06 | Renomear e mover o arquivo para `<pasta base>\<Processo>\` com o nome da RN-03 | Essencial |
| RF-07 | **Perfis** de configuração: cada perfil define a rotina, o modelo de filtro, o formato, o modo das filiais, a lista padrão de filiais e o nome do processo | Essencial |
| RF-08 | Tratar o erro **"perda de comunicação com o servidor"**: esperar a mensagem sumir (com tempo máximo) e continuar | Essencial |
| RF-09 | Tratar o erro **mensagem vermelha**: fechar a mensagem, fechar e reabrir a tela do relatório, tentar de novo | Essencial |
| RF-10 | Tentar **até 3 vezes no total** por filial; se ainda falhar, registrar e **seguir para a próxima filial** sem parar a execução | Essencial |
| RF-11 | **Log** de cada execução (início, fim, filial, etapa, erro, print da tela no momento do erro) | Essencial |
| RF-12 | **Aviso no Telegram** quando uma filial/automação falhar e um resumo ao fim da execução | Importante |
| RF-13 | **Resumo da execução** (sucessos e falhas por filial), que o usuário usa para rodar de novo só o que falhou | Importante |
| RF-14 | Botão/atalho para **interromper** a automação com segurança (ex.: mover o mouse para o canto da tela) | Importante |
| RF-15 | Rodar de novo apenas as filiais que falharam numa execução anterior | Desejável |
| RF-17 | Informar o **período (De/Até)** a cada execução; sem informar, o padrão é **ontem** (De = Até = ontem) | Essencial |
| RF-18 | **Grupos de filiais** configuráveis (RN-11) para escolher várias filiais de uma vez | Essencial |
| RF-16 | Interface visual para escolher a automação, o perfil e as filiais e ver o histórico/erros | Desejável (pós-teste; ver Fora do escopo) |

## 5. Regras de negócio
- **RN-01 — Filiais ativas (22):** 3, 4, 6, 9, 12, 13, 14, 17, 18, 19, 20, 21, 30, 31, 60, 69, 71, 72, 73, 74, 75, 76. Essa lista fica numa configuração editável.
- **RN-02:** a cada execução o usuário escolhe as filiais (números e/ou grupos), o modo (individual, por grupo ou consolidado), o período e o formato. O perfil traz os padrões.
- **RN-03 — Nome do arquivo:** `<Processo>_<período>_<escopo>.<ext>`.
  - **Período:** `AAAA-MM-DD` quando De = Até; `AAAA-MM-DD_a_AAAA-MM-DD` quando é um intervalo.
  - **Escopo:** `F03` (individual), o nome do grupo (por grupo, ex.: `Seneto`) ou `Consolidado`.
  - Exemplos: `CurvaABC_2026-11-09_F03.xlsx`, `CurvaABC_2026-10-01_a_2026-10-31_Seneto.pdf`.
- **RN-04 — Pasta:** cada processo tem sua subpasta dentro de uma pasta base configurável.
- **RN-05:** se já existir um arquivo com o mesmo nome, o novo **não sobrescreve**. Ele ganha o sufixo `_2`, `_3`, etc.
- **RN-06:** a execução começa sempre na tela inicial do SGLinear, com o usuário já logado. O robô **não digita login nem senha**.
- **RN-07 — Retentativas:** 3 tentativas no total por filial (1 tentativa normal + 2 retentativas). Depois disso, a filial fica como **falha** e a execução segue.
- **RN-08:** variações de um mesmo relatório que só mudam filtros viram **perfis**, não código novo. Código novo só surge para um relatório com uma tela diferente (nova **rotina**).
- **RN-09:** o arquivo só conta como sucesso depois de chegar ao PC e ser movido/renomeado.
- **RN-10:** durante a execução, o PC fica dedicado ao robô (sem uso do mouse ou teclado por pessoas).
- **RN-11 — Grupos de filiais** (configuração editável):
  - **Seneto:** 3, 4, 6, 9, 12, 13, 14, 17, 18, 19, 20, 21 (as ativas entre 3 e 21);
  - **Elenice:** 60;
  - **KazzaPop:** 30, 31;
  - **Arunas:** 69, 71, 72, 73, 74, 75, 76 (as ativas entre 68 e 76).
- **RN-12 — Formato "os dois":** a mesma tela de visualização é exportada duas vezes (PDF e Excel). O item só conta como sucesso se os dois arquivos chegarem.

## 6. Fora do escopo (V1)
1. **Interface visual** para gerenciar as automações. Fica para depois da fase de testes (RF-16). Na V1, a execução é por comando/atalho.
2. **Agendamento automático** (rodar sozinho em horários). Na V1, a execução é manual.
3. **Login automático** no ERP ou no Terminal Server.
4. **Outros módulos** além de relatórios (ex.: lançamentos, cadastros, notas).
5. **Tratar ou analisar o conteúdo** dos relatórios (somar, cruzar, gerar painéis). A V1 só baixa e organiza.
6. **Vários usuários ou máquinas** rodando ao mesmo tempo.
7. Enviar os relatórios por e-mail ou subir para nuvem/Drive.
8. Tratar erros do ERP **ainda não conhecidos**. Eles só são registrados em log e avisados. Novos tratamentos entram aos poucos.

## 7. Riscos
| Risco | Impacto | Mitigação inicial |
|---|---|---|
| Reconhecimento por imagem quebra se a resolução, o zoom ou o tema da tela mudarem | Alto | Fixar a resolução/zoom e documentar no TRD; guardar as imagens de referência por versão |
| Atualização do SGLinear muda telas ou ícones | Médio | Imagens de referência fáceis de trocar; log com print do erro |
| Lentidão do servidor/Terminal Server | Médio | Esperas inteligentes (aguardar a imagem aparecer) em vez de tempos fixos |
| Janela "Descarregar arquivo"/download do Chrome muda de comportamento | Médio | Validar no teste da Curva ABC e documentar o caminho |
| Alguém usar o PC durante a execução | Médio | RN-10 e parada de emergência (RF-14) |
| Erros novos do ERP | Médio | Log com print + aviso no Telegram |

## 8. Dúvidas em aberto
- ~~D-01~~ (resolvida): Relatórios → Relatórios Gerenciais → Curva ABC / Contribuição Marginal de Venda; modelo "Curva ABC".
- D-02: **pasta base** dos relatórios (sugestão: `D:\Relatorios\`).
- ~~D-03~~ (resolvida): o robô marca as filiais na lista do "+" do campo Filial.
- D-04: textos e aparência exatos das mensagens de erro ("perda de comunicação" e "mensagem vermelha"). Prints delas ajudam muito.
- D-05: tempo máximo de espera para a "perda de comunicação" antes de contar como falha (sugestão: 3 minutos).
- ~~D-06~~ (resolvida): 1920x1080, escala 100%, zoom 100%.
- D-07: o bot do Telegram ainda vai ser criado (token + chat). Os dados ficam num arquivo local fora do GitHub.

---

## Histórico de mudanças
| Versão | Data | Mudança |
|---|---|---|
| 0.1 | 2026-11-10 | Primeiro rascunho a partir da entrevista e do vídeo do Relatório de Produtos |
| 1.0 | 2026-11-10 | Aprovado pelo usuário |
| 1.1 | 2026-11-10 | Período De/Até (RF-17), grupos de filiais (RF-18, RN-11), modo por grupo, formato PDF/Excel/ambos por execução (RN-12), novo padrão de nome (RN-03); D-01, D-03 e D-06 resolvidas |
