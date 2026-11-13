# Plano de Implantação — Automações Linear

- **Versão:** 1.14
- **Data:** 2026-11-10
- **Status:** aprovado
- **Base:** PRD, TRD, Fluxo, Design e Backend v1.0

---

**Regra:** só avançamos para a próxima etapa depois que a atual for testada por você e você confirmar. Ao fim de cada etapa:
- o código vai para o GitHub (`G-Mitter/automacoes-Linear`);
- os documentos afetados são atualizados.

**Status possíveis:** pendente / em andamento / testada / concluída.

| Etapa | Resumo | Status |
|---|---|---|
| E1 | Esqueleto do projeto + GitHub + pré-checagem | concluída |
| E2 | Captura das imagens de referência da Curva ABC | concluída |
| E3 | Rotina da Curva ABC para 1 filial (até baixar no PC) | concluída |
| E4 | Organizar o arquivo (nome + pasta) | concluída |
| E5 | Várias filiais: individual, por grupo e consolidado + formato "ambos" + histórico + resumo | concluída |
| E6 | Tratamento de erros e retentativas | em andamento |
| E7 | Telegram + `rerun` + limpeza de logs | pendente |
| E8 | Teste de aceitação com as 22 filiais | pendente |

---

## E1 — Esqueleto do projeto + GitHub + pré-checagem
- **Objetivo:** ter algo que roda: o comando lista os perfis e confere se a tela está pronta, **sem clicar em nada**.
- **O que será construído:**
  - estrutura de pastas do TRD, `requirements.txt` (pyautogui, opencv-python, pyyaml, requests, rich), `.gitignore`, `.env.example` e `README`;
  - `config/geral.yaml` com as 22 filiais e `config/perfis/curva_abc.yaml` (provisório);
  - CLI: `.\linear perfis` e `.\linear checar`;
  - a checagem confere a resolução de 1920x1080, se os perfis e as filiais são válidos (validações do Backend §4) e se a pasta base existe;
  - parada de emergência ativa;
  - `git init`, primeiro commit e push para o GitHub.
- **RF/T/dados:** RF-07, RF-14 (base); T-01; Geral e Perfil.
- **Como testar:**
  1. `cd C:\repositorios\automacaoLinear`, depois `.venv\Scripts\activate`.
  2. `.\linear perfis` deve mostrar "Curva ABC" com os padrões.
  3. `.\linear checar` deve mostrar ✅ na resolução e ✅ na configuração.
  4. Mude a escala do Windows para 125% e rode `checar` de novo: deve aparecer ❌ resolução. Depois volte para 100%.
  5. Abra o repositório no GitHub e confira que estão lá o código e os docs, mas não o `.env`.
- **Pronto quando:** os 5 passos passarem.
- **Risco:** baixo. Pode faltar a permissão de push no GitHub: você faz login no `gh` uma vez.

## E2 — Captura das imagens de referência (Curva ABC)
- **Objetivo:** ter todos os recortes de tela de que a rotina precisa.
- **O que será construído:**
  - `.\linear capturar <nome>`: depois de uma contagem regressiva, tira um print da tela inteira (salvo em `capturas/`, fora do Git). O Claude recorta os elementos a partir desses prints;
  - `assets/imagens/catalogo.yaml`;
  - recortes da tela inicial, do menu até a Curva ABC, do campo de modelo, do Filial "+", de Desmarcar todos, de Confirmar, de Confirma, de Exportar Relatório, do Tipo PDF/Excel, de Salvar, de Descarregar arquivo, de Abrir e das duas mensagens de erro (se aparecerem);
  - `.\linear checar` passa a conferir se cada imagem é **encontrada na tela atual**, sem clicar.
- **Dependências (você):**
  - o caminho do menu da Curva ABC (D-01);
  - o modelo de filtro salvo no ERP, com o nome dele;
  - a confirmação de escala 100% e zoom 100%.
- **RF/T/dados:** RF-02; E-01 a E-08; Imagem.
- **Como testar:**
  1. Abra a tela da Curva ABC.
  2. Rode `.\linear checar --tela abc` e, nos 5 segundos de contagem, volte para o Chrome. Cada imagem dessa tela deve mostrar ✅ "encontrada".
  3. Repita com cada tela aberta: `inicial`, `menu`, `filtros`, `filial`, `visualizacao`, `exportar` e `descarregar`.
  4. Revise os PNG em `assets/imagens/`: não pode haver dados de clientes, produtos ou valores.
- **Pronto quando:** todas as imagens forem encontradas com confiança ≥ 0,9 e você tiver revisado os recortes.
- **Risco:** médio. Algumas janelas podem abrir em posições diferentes, o que já é coberto por buscar na tela toda.

## E3 — Rotina da Curva ABC para 1 filial
- **Objetivo:** o robô faz E-01 → E-08 sozinho para **uma filial** e o arquivo chega na pasta Downloads.
- **O que será construído:** a camada de tela (`tela.py`, com esperas inteligentes) e a rotina `relatorio_padrao.py`. Comando: `.\linear run curva_abc --filiais 3`.
- **RF/T/dados:** RF-01 a RF-05, RF-17; E-01 a E-08 (incluindo E-03b); Perfil.
- **Inclui:** as opções `--de`/`--ate` (padrão: ontem).
- **Como testar:**
  1. Deixe o SGLinear na tela inicial e rode o comando.
  2. Solte o mouse e observe.
  3. Deve abrir a Curva ABC, escolher o modelo, marcar só a F03, confirmar, exportar no formato do perfil e descarregar.
  4. Confira se o arquivo chegou em Downloads e se abre corretamente.
  5. Teste a parada de emergência levando o mouse ao canto superior esquerdo no meio da execução.
- **Pronto quando:** funcionar 3 vezes seguidas sem intervenção e a parada de emergência funcionar.
- **Risco:** alto. É a etapa em que o reconhecimento de imagem é posto à prova, e ajustes de imagens e tempos são esperados.

## E4 — Organizar o arquivo
- **Objetivo:** o arquivo baixado vai para `<pasta base>\CurvaABC\CurvaABC_AAAA-MM-DD_F03.xlsx`.
- **O que será construído:** `downloads.py` (pega o arquivo novo e completo, inclusive `nome (1).xlsx`) e `organizador.py` (renomeia, cria a pasta e aplica os sufixos `_2` e `_3`, RN-05).
- **RF/T/dados:** RF-05, RF-06; Geral.
- **Como testar:**
  1. Rode a F03 duas vezes no mesmo dia.
  2. Devem aparecer `CurvaABC_2026-xx-xx_F03.xlsx` e `..._F03_2.xlsx` na pasta.
  3. A pasta Downloads não deve ficar com o arquivo solto.
- **Pronto quando:** os nomes, a pasta e os sufixos estiverem corretos.
- **Risco:** baixo.

## E5 — Várias filiais: individual, por grupo e consolidado
- **Objetivo:** rodar uma lista de filiais (números e/ou grupos) nos três modos, nos formatos PDF, Excel ou ambos, com histórico e resumo.
- **O que será construído:** o orquestrador (sem retentativas ainda), `execucoes/<id>.json`, a barra de progresso e a tabela de resumo (Design §3).
- **RF/T/dados:** RF-03, RF-04, RF-11, RF-13, RF-18; T-01, T-03; Geral.grupos, Execucao e ItemExecucao.
- **Testes extras:** `--filiais kazzapop --modo por_grupo` gera 1 arquivo `_KazzaPop`; `--formato ambos` gera PDF e Excel.
- **Como testar:**
  1. `.\linear run curva_abc --filiais 3,4,6 --modo individual` deve gerar 3 arquivos (F03, F04, F06).
  2. `.\linear run curva_abc --filiais 3,4,6 --modo consolidado` deve gerar 1 arquivo, e o relatório deve mostrar as 3 filiais.
  3. Abra o JSON da execução e confira os status.
- **Pronto quando:** os dois modos estiverem corretos e o resumo bater com os arquivos.
- **Risco:** médio. A seleção de várias filiais (D-03) ainda precisa ser confirmada.

## E6 — Tratamento de erros e retentativas
- **Objetivo:** os erros conhecidos são tratados e a execução nunca para por causa de uma filial.
- **O que será construído:**
  - `erros.py`, o vigia de erros: perda de comunicação, mensagem vermelha, tempo esgotado, sem dados e modelo não encontrado;
  - as 3 tentativas;
  - fechar e reabrir as telas entre as tentativas;
  - print da tela a cada erro.
- **Dependências (você):** prints das duas mensagens de erro (D-04) e, se possível, da mensagem de "sem dados".
- **RF/T/dados:** RF-08, RF-09, RF-10, RF-11; Fluxo §4.
- **Como testar (erros simulados):**
  1. Durante uma execução, abra uma janela do Bloco de Notas por cima. O robô não acha o botão, tenta de novo e se recupera.
  2. Use uma filial inexistente no perfil de teste: deve aparecer FALHA após 3 tentativas e a próxima filial deve rodar.
  3. Quando um erro real do Linear acontecer, confira no log o tratamento correto.
- **Pronto quando:** os testes 1 e 2 passarem, cada erro tiver um print salvo e a execução sempre chegar ao fim.
- **Risco:** alto. Os erros reais são intermitentes, então a validação completa pode levar alguns dias de uso.

## E7 — Telegram + `rerun` + limpeza de logs
- **Objetivo:** aviso no celular e refazer só o que falhou.
- **O que será construído:** `telegram.py` (formato do Design §4), `.\linear rerun <id>` e a limpeza dos logs com mais de 90 dias.
- **Dependências (você):** criar o bot no @BotFather e enviar o token e o chat_id. Eu passo o passo a passo.
- **RF/T/dados:** RF-12, RF-15; T-02.
- **Como testar:**
  1. Force uma falha, como na E6. A mensagem ❌ deve chegar no Telegram, seguida do resumo.
  2. Rode `.\linear rerun <id>`: só a filial que falhou roda de novo.
  3. Desligue a internet: a automação deve continuar, com o aviso de falha no envio registrado no log.
- **Pronto quando:** os 3 testes passarem.
- **Risco:** baixo.

## E8 — Teste de aceitação (22 filiais)
- **Objetivo:** validar o uso real.
- **O que será construído:** nada novo. Só ajustes finos de tempos e imagens, a versão final do README e a revisão dos documentos.
- **Como testar:**
  1. `.\linear run curva_abc --filiais todas --modo individual`: 22 arquivos ou falhas registradas, sem a execução travar.
  2. Repita em `--modo consolidado`.
  3. Repita em 3 dias diferentes.
- **Pronto quando:** pelo menos 95% das filiais tiverem sucesso sem intervenção e toda falha estiver no log, no Telegram e no resumo.
- **Risco:** médio.

---

## UI1 — Bolinha flutuante, bandeja e painel (iniciar + acompanhar + erros)
- **Objetivo:** o usuário deixa de precisar do terminal. Um app sempre ligado, com ícone na bandeja do Windows; uma bolinha flutua no canto superior direito **sobre qualquer janela** enquanto uma automação roda, e muda de cor conforme o status. Clicar na bolinha (ou no ícone da bandeja) abre um painel para escolher e iniciar um perfil, ver o progresso da execução atual e listar os erros que apareceram (Design §9b).
- **O que será construído:** `linear/ui/app.py` (PySide6: ícone de bandeja + bolinha sem moldura, sempre no topo, translúcida) e `linear/ui/painel.py` (lista de perfis com botão Iniciar, que chama o mesmo `python -m linear run` como subprocesso; tabela de progresso e lista de erros lendo `execucoes/*.json`, sem precisar mudar o robô). Atalho `linear_ui.cmd` para abrir.
- **RF/T/dados:** RF-16; TRD §1 (PySide6); Design §9b; Execucao/ItemExecucao (leitura, sem mudança de formato).
- **Como testar:**
  1. Abrir `linear_ui.cmd`: aparece o ícone na bandeja, sem bolinha (nada rodando).
  2. Pelo painel, escolher "Curva ABC", filiais `3,4`, Iniciar: a bolinha aparece no canto superior direito, por cima do Chrome/ERP, e muda de cor ao terminar.
  3. Clicar na bolinha durante a execução: o painel mostra a filial atual e o progresso.
  4. Forçar uma falha (ex.: filial inexistente): o painel lista o erro com filial, hora e o caminho do print.
- **Pronto quando:** os 4 testes passarem e o app sobreviver a iniciar e cancelar duas execuções seguidas sem travar.
- **Risco:** médio. É a primeira peça gráfica do projeto; pode exigir mais um ciclo de ajuste visual depois do primeiro teste.

## UI2 — Agendamento e automações futuras no painel
- **Objetivo:** o painel vira o único lugar para cadastrar e agendar as automações que forem chegando, não só a Curva ABC.
- **O que será construído:** decidido quando houver uma 2ª rotina pronta para entrar no painel.
- **Risco:** baixo.

---

## Depois da V1 (fora deste plano)
- Novos perfis e relatórios: cada um é um perfil novo ou uma rotina nova, mais a captura de imagens (repete E2 a E3 de forma reduzida).
- Interface visual (RF-16): UI1 e UI2 acima cobrem a 1ª versão (bolinha + painel). Passos seguintes entram aqui conforme surgirem.

---

## Histórico de mudanças
| Versão | Data | Mudança |
|---|---|---|
| 1.14 | 2026-11-13 | UI1: ao Iniciar, o painel se esconde e o ERP volta à frente sozinho (`janelas.py`, `Geral.janela_erp`); a bolinha se traz de volta ao topo a cada ciclo |
| 1.13 | 2026-11-13 | UI1 ajustada: bolinha no canto inferior direito; aba Automações virou árvore Categoria > Perfil (ex.: Relatórios > Curva ABC), cada um com seu formulário; o painel abre sozinho na aba Erros assim que uma filial falha |
| 1.12 | 2026-11-13 | Novo bloco UI1/UI2: interface visual (RF-16) com bolinha flutuante, bandeja e painel |
| 1.11 | 2026-11-13 | E5 confirmada no ERP (até 7 filiais seguidas, com pausa externa registrada). E6 em andamento: até 3 tentativas por filial, fecha e reabre as telas entre elas, descarta arquivo parcial de tentativa que falhou; a cada tentativa grava tipo, mensagem e print em `ItemExecucao.erros` |
| 0.1 | 2026-11-10 | Primeiro rascunho |
| 1.0 | 2026-11-10 | Aprovado |
| 1.1 | 2026-11-10 | E1 em andamento |
| 1.10 | 2026-11-12 | E4 testada e concluída. E5 construída: `--modo`, formato `ambos`, histórico em `execucoes/`, resumo; adiantado da E6: se um relatório falha, fecha as telas e segue para o próximo |
| 1.9 | 2026-11-12 | E4 construída: `organizador.py` (nome RN-03, pasta do processo, sufixos RN-05) ligado ao `run` |
| 1.8 | 2026-11-12 | E3 testada pelo usuário (3 execuções seguidas e parada de emergência) e concluída |
| 1.7 | 2026-11-10 | E3 construída: `tela.py`, rotina `relatorio_padrao`, `downloads.py`, comando `run` (individual, sem retentativas, para no 1º erro) e opção `--depurar` |
| 1.6 | 2026-11-10 | E2 testada pelo usuário e concluída. A imagem `pasta_robo` passa a ser conferida depois da navegação, e será testada na E3 |
| 1.5 | 2026-11-10 | E2: 26 recortes validados contra os prints. Barra do Terminal Server por posição fixa; tipo de arquivo escolhido pelo teclado; nomes das telas para o `checar --tela` |
| 1.4 | 2026-11-10 | E2 em andamento. Captura por print de tela inteira (`.\linear capturar`) e recorte feito pelo Claude |
| 1.3 | 2026-11-10 | E3 passa a incluir o período (`--de/--ate`); E5 inclui grupos, modo por grupo e formato "ambos" |
| 1.2 | 2026-11-10 | E1 testada pelo usuário e concluída; execução via `.\linear` (atalho linear.cmd) |
