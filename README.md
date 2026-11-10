# Automações Linear

Robô (RPA) para o ERP SGLinear acessado via Terminal Server no Chrome. Reconhece imagens na tela e usa mouse/teclado para tirar relatórios, exportar e organizar os arquivos.

Documentação completa em [`docs/`](docs/) (PRD, TRD, Fluxo, Design, Backend, Plano).

## Instalação (uma vez)
```powershell
cd C:\repositorios\automacaoLinear
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env   # preencha o Telegram (etapa E7)
```

## Uso
```powershell
.venv\Scripts\activate
python -m linear perfis   # lista os perfis
python -m linear checar   # confere tela (1920x1080, escala 100%) e configuração
```

**Parada de emergência:** leve o mouse ao canto superior esquerdo da tela.

## Requisitos de tela
Resolução 1920x1080, escala do Windows 100%, zoom do Chrome 100%.
