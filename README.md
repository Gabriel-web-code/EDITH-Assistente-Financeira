# EDITH - Assistente Financeira

Chatbot de gestão financeira com IA. Registra gastos por conversa, mantém memória
permanente, monta a tabela mensal de despesas e consulta informações atuais do
mercado na internet.

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

O Streamlit não roda no Vercel. O Vercel executa apenas funções curtas que
exportam `app`, `application` ou `handler` (WSGI/ASGI), e encerra o processo ao
fim de cada requisição. O Streamlit precisa de um servidor Python permanente,
com conexão WebSocket aberta e estado por sessão. Por isso o erro
`PYTHON_ENTRYPOINT_NOT_FOUND` aparece: não existe um objeto `app` para exportar.

### Vercel (versão nativa, sem Python)

A pasta `vercel/` contém uma versão feita para o Vercel: interface estática
(`index.html`, `styles.css`, `app.js`) e uma função serverless
(`api/chat.js`) que chama a Groq e executa as mesmas ferramentas.

O caminho mais rápido:

```powershell
cd vercel
npx vercel
npx vercel env add GROQ_API_KEY production
npx vercel --prod
```

No primeiro comando, aceite criar o projeto. No segundo, cole a chave da Groq
quando for solicitado. O guia completo está em `vercel/README.md`.

Nessa versão, conversas, gastos e memórias ficam no `localStorage` do
navegador, porque funções serverless não mantêm disco. Para usar os mesmos
dados em vários dispositivos, será necessário um banco externo.

### Streamlit Community Cloud (para o app Python)

1. Envie o projeto para um repositório no GitHub, sem `.env`, `.venv` e `edith.db`.
2. Acesse https://share.streamlit.io e clique em **New app**.
3. Escolha o repositório, a branch e o arquivo `app.py`.
4. Em **Advanced settings > Secrets**, cole:

```toml
GROQ_API_KEY = "sua-chave-da-groq"
```

5. Clique em **Deploy**.

### Render (para o app Python, com o `render.yaml` já incluído)

1. Envie o projeto para o GitHub.
2. Acesse https://render.com, clique em **New > Web Service** e conecte o repositório.
3. O Render lê o `render.yaml` e já configura o comando de inicialização.
4. Em **Environment**, crie a variável `GROQ_API_KEY` com a sua chave.

O plano gratuito do Render hiberna após alguns minutos sem acesso; a primeira
abertura seguinte demora cerca de um minuto.

**Atenção aos dados**: no app Python hospedado, o arquivo `edith.db` fica em um
disco temporário. Gastos, memórias e conversas podem ser apagados quando o app
for reiniciado ou atualizado. Para uso real, mantenha os dados no seu computador
ou migre o banco para um serviço externo, como Postgres ou Turso.

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

Tudo é salvo localmente no arquivo `edith.db`, no formato SQLite:

| Tabela | Conteúdo |
| --- | --- |
| `conversas` | Título e datas de cada conversa |
| `mensagens` | Histórico completo de cada conversa |
| `gastos` | Despesas com descrição, valor, categoria e data |
| `memorias` | Fatos permanentes informados por você |

Para fazer backup, copie o arquivo `edith.db`. Para começar do zero, apague o
arquivo ou use os botões do painel. O arquivo não vai para o Git.

## Como funciona

1. `agent.py` monta o prompt fixo da EDITH com a data atual e as memórias salvas.
2. O modelo recebe ferramentas e decide quando usá-las.
3. `db.py` grava e consulta gastos, mensagens e memórias no SQLite.
4. `web.py` pesquisa na internet e lê páginas quando o modelo pede dados atuais.
5. `app.py` desenha a interface e salva cada mensagem no banco.

As ferramentas disponíveis para o agente são: `registrar_gasto`, `listar_gastos`,
`resumo_mensal`, `excluir_gasto`, `salvar_memoria`, `pesquisar_web` e
`abrir_pagina`.

## Arquivos

| Arquivo | Função |
| --- | --- |
| `app.py` | Interface web com o painel financeiro |
| `chatbot.py` | Versão de terminal |
| `agent.py` | Cérebro do agente, prompt e ferramentas |
| `db.py` | Banco de dados SQLite |
| `web.py` | Busca na internet e leitura de páginas |
| `requirements.txt` | Dependências |
| `.env` | Chave da API, não compartilhar |
| `.env.example` | Modelo do `.env` |
| `edith.db` | Dados locais, gerado automaticamente |
| `.streamlit/config.toml` | Tema escuro base da interface |
| `iniciar.bat` | Instala e roda no Windows com dois cliques |
| `.vscode/launch.json` | Atalhos F5 |

## Erros comuns

| Erro | Solução |
| --- | --- |
| `401 Invalid API Key` | Gere outra chave em https://console.groq.com/keys e atualize o `.env` |
| `429 Rate limit` | Aguarde alguns segundos e tente novamente |
| `ModuleNotFoundError` | Ative o `.venv` e rode `pip install -r requirements.txt` |
| Busca sem resultados | A fonte pode ter bloqueado a consulta; tente reformular o pedido |
| Resposta sem dados atuais | Peça explicitamente para pesquisar na internet |

## Privacidade

- A chave em `.env` dá acesso à sua conta na Groq. Não compartilhe o arquivo.
- `edith.db` contém seus gastos e memórias. Também não deve ser compartilhado.
- As mensagens são processadas pela Groq e as buscas são enviadas ao provedor de pesquisa.

> As análises financeiras têm caráter educativo e não constituem recomendação formal de investimento.
