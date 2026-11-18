# EDITH no Vercel

Esta pasta é uma versão nativa de Vercel do projeto: frontend estático
(`index.html`, `styles.css`, `app.js`) e uma função serverless
(`api/chat.js`) que conversa com a API da Groq.

O Vercel não executa Streamlit. Ele espera uma aplicação WSGI/ASGI com uma
variável `app`, `application` ou `handler`, e encerra o processo ao fim de cada
requisição. Por isso o erro `PYTHON_ENTRYPOINT_NOT_FOUND`. Esta pasta resolve o
problema sem depender de Python.

## O que está aqui

```
index.html      Interface (mesmo visual escuro do app original)
styles.css      Estilos
app.js          Conversa, histórico, painel financeiro e memória no navegador
api/chat.js     Função serverless: Groq, ferramentas e busca na web
vercel.json     Configuração de deploy
package.json    Metadados e versão do Node
.env.example    Modelo das variáveis de ambiente
```

## Como funciona

1. O navegador guarda conversas, gastos e memórias no `localStorage`.
2. A cada mensagem, o navegador envia o histórico e o estado financeiro para
   `/api/chat`.
3. A função chama a Groq com as ferramentas `registrar_gasto`, `listar_gastos`,
   `resumo_mensal`, `excluir_gasto`, `salvar_memoria`, `pesquisar_web` e
   `abrir_pagina`.
4. O estado atualizado volta para o navegador e o painel é redesenhado.

A chave da Groq fica somente no servidor, como variável de ambiente. Ela nunca
aparece no código do site.

## Deploy pela CLI (mais rápido)

Requisitos: Node.js 20 ou superior e uma conta no Vercel.

```powershell
cd "C:\Users\0404g\OneDrive\Documentos\Projeto Padrão\vercel"
npx vercel
```

Na primeira execução:

1. Confirme o login no navegador.
2. Aceite criar um novo projeto.
3. Nome do projeto: `edith`.
4. Diretório raiz: `./`.
5. Build Command: deixe vazio.
6. Output Directory: deixe vazio.

Depois cadastre a chave e publique em produção:

```powershell
npx vercel env add GROQ_API_KEY production
npx vercel env add GROQ_API_KEY preview
npx vercel --prod
```

Quando o comando pedir o valor, cole a chave da Groq
(https://console.groq.com/keys).

Opcional, para trocar o modelo:

```powershell
npx vercel env add GROQ_MODEL production
```

Valor: `openai/gpt-oss-120b`.

## Deploy pelo GitHub

1. Crie um repositório e envie o conteúdo **desta pasta** (`vercel/`) para a
   raiz do repositório. Não envie `.env`, `.env.local` nem `.vercel`.
2. Em https://vercel.com, clique em **Add New > Project** e importe o
   repositório.
3. Em **Framework Preset**, escolha **Other**.
4. Deixe **Build Command** e **Output Directory** vazios.
5. Em **Environment Variables**, crie:
   - `GROQ_API_KEY` com a sua chave;
   - `GROQ_MODEL` com `openai/gpt-oss-120b` (opcional).
6. Clique em **Deploy**.

Se preferir manter o projeto Python no mesmo repositório, importe o repositório
e defina **Root Directory** como `vercel`.

## Rodar localmente

```powershell
cd "C:\Users\0404g\OneDrive\Documentos\Projeto Padrão\vercel"
Copy-Item .env.example .env.local
# edite .env.local e cole a chave real
npx vercel dev
```

O site abre em http://localhost:3000.

## Limites e observações

- O plano gratuito do Vercel permite funções de até 60 segundos. O
  `vercel.json` já define `maxDuration: 60`.
- Cada resposta pode envolver várias chamadas à Groq. O código limita a quatro
  rodadas e 20 segundos por chamada para caber no tempo da função.
- Gastos, conversas e memórias ficam no navegador do usuário, não no servidor.
  Limpar os dados do site apaga tudo.
- Para usar em vários dispositivos com os mesmos dados, será necessário migrar
  o estado para um banco externo, como Postgres ou Turso.
- A busca na internet usa o DuckDuckGo em HTML. Se ele bloquear a requisição, a
  EDITH informa que não conseguiu consultar, sem inventar dados.
