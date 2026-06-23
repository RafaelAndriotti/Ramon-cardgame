# 🃏 Ramon Card Game
 
Um jogo de cartas desenvolvido em Python com interface gráfica, banco de dados local e executável standalone gerado com PyInstaller.
 
---
 
## 📋 Índice
 
- [Sobre o Projeto](#sobre-o-projeto)
- [Tecnologias Utilizadas](#tecnologias-utilizadas)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Pré-requisitos](#pré-requisitos)
- [Como Instalar e Rodar](#como-instalar-e-rodar)
  - [Opção 1 — Executar pelo código-fonte (Python)](#opção-1--executar-pelo-código-fonte-python)
  - [Opção 2 — Executar o executável compilado](#opção-2--executar-o-executável-compilado)
- [Como Jogar](#como-jogar)
- [Banco de Dados](#banco-de-dados)
- [Como Gerar o Executável](#como-gerar-o-executável)
- [Contribuindo](#contribuindo)
---
 
## Sobre o Projeto
 
Ramon Card Game é um jogo de cartas desenvolvido como projeto acadêmico. O jogo possui um motor próprio (`GameEngine`) localizado na pasta `src/`, sistema de persistência de dados via SQLite e assets visuais organizados na pasta `assets/`.
 
---
 
## Tecnologias Utilizadas
 
- **Python 3.x** — Linguagem principal
- **SQLite** — Banco de dados local (`game_data.db`)
- **PyInstaller** — Geração do executável standalone
- **Módulo `src/engine`** — Motor do jogo desenvolvido internamente
---
 
## Estrutura do Projeto
 
```
Ramon-cardgame/
│
├── main.py                  # Ponto de entrada do jogo
├── game_data.db             # Banco de dados gerado em tempo de execução (não versionar)
├── Ramon Card Game.spec     # Configuração do PyInstaller (não versionar)
│
├── src/                     # Código-fonte do motor do jogo
│   └── engine.py            # GameEngine — lógica principal
│
├── assets/                  # Imagens, sons e recursos visuais
│
├── build/                   # Pasta gerada pelo PyInstaller (não versionar)
└── dist/                    # Executável final gerado (não versionar)
```
 
---
 
## Pré-requisitos
 
Antes de começar, certifique-se de ter instalado:
 
- [Python 3.8 ou superior](https://www.python.org/downloads/)
- `pip` (gerenciador de pacotes do Python, já incluso com o Python)
Para verificar se o Python está instalado corretamente, abra o terminal e rode:
 
```bash
python --version
```
 
---
 
## Como Instalar e Rodar
 
### Opção 1 — Executar pelo código-fonte (Python)
 
Esta opção é recomendada para quem quer rodar o jogo diretamente pelo terminal ou contribuir com o desenvolvimento.
 
**1. Clone o repositório**
 
```bash
git clone https://github.com/RafaelAndriotti/Ramon-cardgame.git
cd Ramon-cardgame
```
 
**2. (Opcional) Crie um ambiente virtual**
 
Isso evita conflitos com outros projetos Python na sua máquina:
 
```bash
python -m venv venv
```
 
Ative o ambiente virtual:
 
- **Windows:**
```bash
  venv\Scripts\activate
```
- **Linux / Mac:**
```bash
  source venv/bin/activate
```
 
**3. Instale as dependências**
 
```bash
pip install -r requirements.txt
```
 
> Se o arquivo `requirements.txt` não existir, o jogo pode não ter dependências externas. Tente rodar diretamente.
 
**4. Execute o jogo**
 
```bash
python main.py
```
 
---
 
### Opção 2 — Executar o executável compilado
 
Se você baixou ou gerou o executável via PyInstaller, basta localizar o arquivo dentro da pasta `dist/` e executá-lo diretamente — sem precisar do Python instalado.
 
- **Windows:** Dê dois cliques em `Ramon Card Game.exe` dentro de `dist/`
- **Linux / Mac:** Execute via terminal:
```bash
  ./dist/"Ramon Card Game"
```
 
> ⚠️ **Atenção:** A pasta `assets/` precisa estar no mesmo diretório que o executável para que as imagens e sons carreguem corretamente.
 
---
 
## Como Jogar
 
> As instruções abaixo são baseadas na estrutura do jogo. Atualize esta seção com as regras específicas do seu jogo.
 
**Objetivo do jogo**
 
O objetivo principal é [descreva o objetivo aqui — ex: vencer o oponente zerando seus pontos de vida, completar um deck, etc].
 
**Início da partida**
 
1. Ao abrir o jogo, você verá a tela inicial.
2. Escolha uma opção para iniciar uma nova partida ou continuar uma partida salva.
3. Cada jogador começa com um conjunto de cartas em mãos.
**Rodada**
 
- A cada turno, o jogador pode **comprar uma carta** do baralho.
- Em seguida, escolhe **qual carta jogar** da sua mão.
- As cartas possuem atributos como ataque, defesa ou efeitos especiais.
- Após jogar a carta, é a vez do adversário.
**Condição de vitória**
 
O jogo termina quando [descreva aqui — ex: um jogador ficar sem cartas, atingir X pontos, ou o oponente for derrotado].
 
**Controles**
 
| Ação | Controle |
|------|----------|
| Selecionar carta | Clique com o botão esquerdo |
| Confirmar jogada | Tecla `Enter` ou botão de confirmar |
| Cancelar seleção | Tecla `Esc` |
| Sair do jogo | Fechar a janela ou menu de pausa |
 
> ✏️ **Nota para o desenvolvedor:** Preencha os detalhes reais de gameplay nesta seção (regras, número de cartas, tipos de carta, sistema de pontuação etc).
 
---
 
## Banco de Dados
 
O arquivo `game_data.db` é um banco de dados SQLite gerado **automaticamente** pelo jogo na primeira execução. Ele armazena dados como progresso, pontuação e configurações do jogador.
 
- Este arquivo **não deve ser incluído no repositório**.
- Cada jogador terá o seu próprio `game_data.db` gerado localmente.
- Caso queira resetar o progresso, basta deletar o arquivo `game_data.db` e rodar o jogo novamente.
---
 
## Como Gerar o Executável
 
Caso queira recompilar o executável do zero usando PyInstaller:
 
**1. Instale o PyInstaller**
 
```bash
pip install pyinstaller
```
 
**2. Gere o executável usando o arquivo `.spec`**
 
```bash
pyinstaller "Ramon Card Game.spec"
```
 
Ou gere manualmente com:
 
```bash
pyinstaller --onefile --windowed --add-data "assets;assets" main.py
```
 
> O executável final estará na pasta `dist/`.
 
---
 
## Contribuindo
 
1. Faça um fork do projeto
2. Crie uma branch para sua feature: `git checkout -b minha-feature`
3. Faça commit das suas mudanças: `git commit -m 'Adiciona minha feature'`
4. Envie para a branch: `git push origin minha-feature`
5. Abra um Pull Request
---
 
Desenvolvido por [RafaelAndriotti](https://github.com/RafaelAndriotti) e colaboradores.
