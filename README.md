# EDITH - Assistente Financeira

Chatbot de gestão financeira com IA. Registra gastos por conversa, mantém memória
permanente, monta a tabela mensal de despesas e consulta informações atuais do
mercado na internet.

Quando publicado na internet, cada visitante recebe um cofre vazio e exclusivo:
ninguém vê os gastos, as memórias ou as conversas de outra pessoa.

## Recursos

- **Agente financeiro**: responde sobre mercado, investimentos, orçamento e uso do dinheiro.
- **Personalidade fixa**: assistente séria e objetiva de um empresário, sem seleção de personalidade.
- **Cofre de gastos**: registra despesas ditas na conversa e guarda tudo em banco local.
- **Tabela mensal**: total do mês, total por categoria e despesas individuais.
- **Memória permanente**: guarda nome, empresa, metas, preferências e o histórico da conversa.
- **Histórico de conversas**: várias conversas separadas no painel lateral, com troca e exclusão.
- **Acesso à internet**: pesquisa notícias, cotações e indicadores em tempo real e cita as fontes.
- **Interface escura estilo Apple**: degradês em preto, cinza e branco, responsiva para celular, sem emojis.
- **Duas versões**: interface web (Streamlit) e terminal.
- **Privacidade por sessão**: no site, cada aba do navegador trabalha com um banco próprio e vazio.

## Requisitos

- Python 3.10 ou superior
- Chave de API da Groq: https://console.groq.com/keys

## Instalação

A pasta `.venv` não vem no ZIP. Ela é criada no seu computador no primeiro uso,
porque contém caminhos específicos da sua máquina.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Se o PowerShell bloquear a ativação:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

No CMD use `.venv\Scripts\activate.bat`. No Linux ou macOS use
`python3 -m venv .venv` e `source .venv/bin/activate`.

## Configuração

Crie o arquivo `.env` na pasta do projeto:

```env
GROQ_API_KEY=sua_chave_aqui
```

Opcionalmente, escolha outro modelo:

```env
GROQ_MODEL=openai/gpt-oss-120b
```

## Como rodar

No Windows, o caminho mais simples é dar dois cliques em `iniciar.bat`. Ele cria
o ambiente virtual, instala as dependências e abre a interface.

Ou manualmente, com a interface web:

```powershell
streamlit run app.py
```

O navegador abre em http://localhost:8501.

Versão de terminal:

```powershell
python chatbot.py
```

No VS Code, pressione **F5** e escolha **Interface Streamlit** ou
**Chatbot no terminal**.

## Publicar na internet

O Streamlit não roda em hospedagem de arquivos estáticos nem em funções
serverless curtas. Ele precisa de um servidor Python permanente, com conexão
WebSocket aberta e estado por sessão. As duas opções abaixo atendem a esse
requisito.

Antes de publicar, confirme que o repositório **não** contém `.env` nem
`edith.db`. O `.gitignore` já bloqueia os dois.

### Streamlit Community Cloud (recomendado)

1. Envie o projeto para um repositório no GitHub. O repositório usado por este
   projeto é `Gabriel-web-code/EDITH-Assistente-Financeira`.
2. Acesse https://share.streamlit.io e clique em **New app**.
3. Escolha o repositório, a branch `main` e o arquivo `app.py`.
4. Em **Advanced settings > Secrets**, cole:

```toml
GROQ_API_KEY = "sua-chave-da-groq"
```

5. Clique em **Deploy**. O endereço fica no formato
   `https://seu-app.streamlit.app`.

O plano gratuito hiberna o app depois de um período sem visitas. A primeira
abertura seguinte demora alguns segundos.

### Render (alternativa, com o `render.yaml` já incluído)

1. Envie o projeto para o GitHub.
2. Acesse https://render.com, clique em **New > Web Service** e conecte o repositório.
3. O Render lê o `render.yaml` e já configura o comando de inicialização.
4. Em **Environment**, crie a variável `GROQ_API_KEY` com a sua chave.

O plano gratuito do Render hiberna após alguns minutos sem acesso; a primeira
abertura seguinte demora cerca de um minuto.

## Como cada visitante fica isolado

O arquivo `sessao.py` resolve o problema de o site abrir com os dados do dono:

1. Ao abrir o app por um endereço que não seja `localhost`, ele cria uma pasta
   temporária exclusiva (`edith_cofre_...`) com um `edith.db` vazio dentro.
2. O caminho fica em `st.session_state`, que é individual por aba do navegador.
3. O `db.py` guarda esse caminho em uma variável de thread. Cada sessão do
   Streamlit roda em uma thread própria, então uma pessoa nunca lê o banco da outra.
4. O `edith.db` que está na pasta do projeto só é usado quando o app roda na
   sua própria máquina (`localhost`). No site, ele jamais é aberto.
5. Ao clicar em **Apagar meus dados** (botão que só aparece no site), a pasta da
   sessão é removida e um cofre novo e vazio é criado na hora.
6. Pastas de sessões encerradas há mais de 12 horas são apagadas automaticamente.

Consequências práticas:

- Cada visitante começa com total zerado, nenhuma memória e uma conversa em branco.
- Ao recarregar a página ou abrir em outra aba, começa um cofre novo. Os dados
  ficam apenas na aba em que foram criados.
- O servidor não guarda nada de forma permanente: reiniciar o app também apaga
  os cofres temporários.
- No seu computador, nada muda: o `edith.db` continua guardando seus dados entre
  execuções. Se precisar forçar esse modo em outro endereço, defina a variável
  `EDITH_LOCAL=1` antes de iniciar o app.

## Exemplos de uso

- "Gastei 89,90 de internet hoje."
- "Registre 340,50 de supermercado no dia 12."
- "Monte a tabela dos meus gastos deste mês."
- "Qual foi o total de outubro por categoria?"
- "Exclua o lançamento 4."
- "Qual a cotação do dólar e do Ibovespa hoje?"
- "Guarde que minha empresa atua no setor de logística."
- "O que você sabe sobre mim?"

## Onde ficam os dados

Tudo é salvo em um arquivo SQLite:

| Tabela | Conteúdo |
| --- | --- |
| `conversas` | Título e datas de cada conversa |
| `mensagens` | Histórico completo de cada conversa |
| `gastos` | Despesas com descrição, valor, categoria e data |
| `memorias` | Fatos permanentes informados por você |

No seu computador, o arquivo é `edith.db`, na pasta do projeto. Para fazer
backup, copie esse arquivo. Para começar do zero, apague o arquivo ou use os
botões do painel. Ele não vai para o Git.

No site, o arquivo fica em uma pasta temporária do servidor, uma por aba, e é
descartado quando a sessão termina. Nada é compartilhado entre visitantes.## Como funciona

1. `agent.py` monta o prompt fixo da EDITH com a data atual e as memórias salvas.
2. O modelo recebe ferramentas e decide quando usá-las.
3. `db.py` grava e consulta gastos, mensagens e memórias no SQLite.
4. `sessao.py` cria o cofre temporário e exclusivo de cada visitante.
5. `web.py` pesquisa na internet e lê páginas quando o modelo pede dados atuais.
6. `app.py` desenha a interface e salva cada mensagem no banco.

As ferramentas disponíveis para o agente são: `registrar_gasto`, `listar_gastos`,
`resumo_mensal`, `excluir_gasto`, `salvar_memoria`, `pesquisar_web` e
`abrir_pagina`.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `app.py` | Interface web com o painel financeiro |
| `sessao.py` | Cofre temporário e exclusivo de cada visitante |
| `chatbot.py` | Versão de terminal |
| `agent.py` | Cérebro do agente, prompt e ferramentas |
| `db.py` | Banco de dados SQLite |
| `web.py` | Busca na internet e leitura de páginas |
| `requirements.txt` | Dependências |
| `.env` | Chave da API, não compartilhar |
| `.env.example` | Modelo do `.env` |
| `edith.db` | Dados locais, gerado automaticamente e ignorado pelo Git |
| `.streamlit/config.toml` | Tema escuro base da interface |
| `.streamlit/secrets.toml.example` | Modelo dos segredos da hospedagem |
| `render.yaml` | Configuração pronta para publicar no Render |
| `iniciar.bat` | Instala e roda no Windows com dois cliques |
| `.vscode/launch.json` | Atalhos F5 |

## Erros comuns

| Erro | Solução |
| --- | --- |
| `401 Invalid API Key` | Gere outra chave em https://console.groq.com/keys e atualize o `.env` ou o segredo do app |
| `429 Rate limit` | Aguarde alguns segundos e tente novamente |
| `ModuleNotFoundError` | Ative o `.venv` e rode `pip install -r requirements.txt` |
| App do site sem chave | Confira o segredo `GROQ_API_KEY` nas configurações da hospedagem |
| Busca sem resultados | A fonte pode ter bloqueado a consulta; tente reformular o pedido |
| Resposta sem dados atuais | Peça explicitamente para pesquisar na internet |

## Privacidade

- A chave em `.env` dá acesso à sua conta na Groq. Não compartilhe o arquivo.
- `edith.db` contém seus gastos e memórias. Também não deve ser compartilhado e
  nunca é enviado ao GitHub.
- No site publicado, cada visitante usa um banco temporário e vazio. O seu banco
  local jamais é lido pelo app hospedado.
- As mensagens são processadas pela Groq e as buscas são enviadas ao provedor de pesquisa.
- A chave da Groq é a mesma para todos os visitantes do site. Por isso, acompanhe
  o consumo e os limites da sua conta em https://console.groq.com.

> As análises financeiras têm caráter educativo e não constituem recomendação formal de investimento.
