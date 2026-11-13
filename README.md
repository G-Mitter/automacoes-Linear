# Automações Linear

Robô (RPA) para o ERP SGLinear acessado via Terminal Server no Chrome. Reconhece imagens na tela e usa mouse/teclado para tirar relatórios, exportar e organizar os arquivos.

Documentação completa em [`docs/`](docs/) (PRD, TRD, Fluxo, Design, Backend, Plano).

## Instalação (uma vez)
```powershell
cd C:\repositorios\automacaoLinear
py -3.13 -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
copy .env.example .env   # preencha o Telegram (etapa E7)
```

## Uso
Não precisa ativar o ambiente: o atalho `linear.cmd` já usa o Python do `.venv`.
```powershell
cd C:\repositorios\automacaoLinear
.\linear perfis   # lista os perfis
.\linear checar   # confere tela (1920x1080, escala 100%) e configuração
.\linear run curva_abc --filiais 3 --de 2026-11-09 --formato xlsx   # roda o relatório
.\linear run curva_abc --filiais 3 --depurar   # idem, com print a cada passo em logs\prints
```

**Parada de emergência:** leve o mouse ao canto superior esquerdo da tela.

## Requisitos de tela
Resolução 1920x1080, escala do Windows 100%, zoom do Chrome 100%.

## Testar a partir de uma etapa
Deixe o ERP na tela certa e rode, por exemplo, com a visualização do relatório aberta:

    .\linear run curva_abc --filiais 3 --de 2026-11-09 --formato xlsx --a-partir E-07

Para só descarregar um arquivo já exportado: `--a-partir E-08 --nome CurvaABC_F03_151755`.
Etapas: E-01, E-02, E-03, E-03b, E-04, E-04b, E-05, E-07, E-08 (ver docs/03-FLUXO.md).

## App (bandeja + bolinha + painel)
Abra com `linear_ui.cmd` (sem janela de terminal) ou `.\linear ui`. Fica na bandeja do Windows;
uma bolinha aparece no canto superior direito, por cima de qualquer janela, enquanto uma automação
roda (azul = rodando, verde = concluída, vermelha = com falha). Clicar na bolinha ou no ícone da
bandeja abre o painel: escolher e iniciar um perfil, acompanhar a execução atual e ver a lista de
erros (lendo `execucoes/*.json`, sem precisar do terminal).
