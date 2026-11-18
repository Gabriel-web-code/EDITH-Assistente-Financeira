const CHAVE_ESTADO = "edith.estado.v1";
const LIMITE_CONVERSAS = 40;
const LIMITE_MENSAGENS = 200;

const MESES = [
  "Janeiro",
  "Fevereiro",
  "Março",
  "Abril",
  "Maio",
  "Junho",
  "Julho",
  "Agosto",
  "Setembro",
  "Outubro",
  "Novembro",
  "Dezembro",
];

const CATEGORIAS = [
  "Alimentação",
  "Moradia",
  "Transporte",
  "Saúde",
  "Educação",
  "Lazer",
  "Compras",
  "Serviços",
  "Impostos",
  "Investimentos",
  "Outros",
];

const BEM_VINDO =
  "Bem-vindo. Sou a EDITH, sua assistente financeira. Posso registrar despesas, " +
  "organizar o resumo do mês e acompanhar o mercado. Como posso ajudar?";

const moeda = new Intl.NumberFormat("pt-BR", {
  style: "currency",
  currency: "BRL",
});

const app = document.getElementById("app");
const conteudo = document.getElementById("conteudo");
const conversaEl = document.getElementById("conversa");
const historicoEl = document.getElementById("historico");
const cardsEl = document.getElementById("cards");
const tabelaEl = document.getElementById("tabela-area");
const memoriaEl = document.getElementById("memoria-lista");
const mesEl = document.getElementById("mes");
const anoEl = document.getElementById("ano");
const campo = document.getElementById("mensagem");
const formulario = document.getElementById("composer");
const enviarBtn = document.getElementById("enviar");
const abrirMenuBtn = document.getElementById("abrir-menu");
const avisoEl = document.getElementById("aviso");

let enviando = false;
let timerAviso = null;

function novoId() {
  if (window.crypto && typeof window.crypto.randomUUID === "function") {
    return window.crypto.randomUUID();
  }
  return "c" + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
}

function arredondar(valor) {
  return Math.round(Number(valor) * 100) / 100;
}

function escaparHtml(texto) {
  return String(texto)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function inline(texto) {
  const codigos = [];
  let saida = texto.replace(/`([^`\n]+)`/g, (_, codigo) => {
    codigos.push(codigo);
    return `\u0000${codigos.length - 1}\u0000`;
  });
  saida = saida.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>'
  );
  saida = saida.replace(/\*\*([^*]+)\*\*/g, "<strong>$1</strong>");
  saida = saida.replace(/__([^_]+)__/g, "<strong>$1</strong>");
  saida = saida.replace(/(^|[^*])\*([^*\n]+)\*/g, "$1<em>$2</em>");
  saida = saida.replace(
    /\u0000(\d+)\u0000/g,
    (_, indice) => `<code>${codigos[Number(indice)]}</code>`
  );
  return saida;
}

function ehSeparadorTabela(linha) {
  const texto = linha.trim();
  if (!texto.includes("-")) return false;
  if (!/^[|\s:-]+$/.test(texto)) return false;
  const celulas = texto.split("|").filter((celula) => celula.trim());
  return (
    celulas.length > 0 &&
    celulas.every((celula) => /^:?-{2,}:?$/.test(celula.trim()))
  );
}

function dividirLinhaTabela(linha) {
  let texto = linha.trim();
  if (texto.startsWith("|")) texto = texto.slice(1);
  if (texto.endsWith("|")) texto = texto.slice(0, -1);
  return texto.split("|").map((celula) => celula.trim());
}

function alinhamentoTabela(celula) {
  const texto = celula.trim();
  if (texto.startsWith(":") && texto.endsWith(":")) return "center";
  if (texto.endsWith(":")) return "right";
  if (texto.startsWith(":")) return "left";
  return "";
}

function markdown(texto) {
  const linhas = escaparHtml(texto || "")
    .replace(/\r\n/g, "\n")
    .split("\n");
  const blocos = [];
  let i = 0;

  while (i < linhas.length) {
    const linha = linhas[i];

    if (!linha.trim()) {
      i++;
      continue;
    }

    if (linha.trim().startsWith("```")) {
      const linguagem = linha.trim().slice(3).trim();
      i++;
      const codigo = [];
      while (i < linhas.length && !linhas[i].trim().startsWith("```")) {
        codigo.push(linhas[i]);
        i++;
      }
      if (i < linhas.length) i++;
      const classe = linguagem ? ` class="lang-${linguagem}"` : "";
      blocos.push(`<pre><code${classe}>${codigo.join("\n")}</code></pre>`);
      continue;
    }

    const titulo = linha.match(/^(#{1,4})\s+(.*)$/);
    if (titulo) {
      const nivel = titulo[1].length;
      blocos.push(`<h${nivel}>${inline(titulo[2])}</h${nivel}>`);
      i++;
      continue;
    }

    if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(linha)) {
      blocos.push("<hr>");
      i++;
      continue;
    }

    if (
      linha.includes("|") &&
      i + 1 < linhas.length &&
      ehSeparadorTabela(linhas[i + 1])
    ) {
      const cabecalho = dividirLinhaTabela(linha);
      const alinhamentos = dividirLinhaTabela(linhas[i + 1]).map(
        alinhamentoTabela
      );
      i += 2;
      const corpo = [];
      while (i < linhas.length && linhas[i].trim() && linhas[i].includes("|")) {
        corpo.push(dividirLinhaTabela(linhas[i]));
        i++;
      }
      let html = '<div class="tabela-rolagem-msg"><table><thead><tr>';
      cabecalho.forEach((celula, indice) => {
        const estilo = alinhamentos[indice]
          ? ` style="text-align:${alinhamentos[indice]}"`
          : "";
        html += `<th${estilo}>${inline(celula)}</th>`;
      });
      html += "</tr></thead><tbody>";
      for (const linhaCorpo of corpo) {
        html += "<tr>";
        cabecalho.forEach((_, indice) => {
          const estilo = alinhamentos[indice]
            ? ` style="text-align:${alinhamentos[indice]}"`
            : "";
          html += `<td${estilo}>${inline(linhaCorpo[indice] || "")}</td>`;
        });
        html += "</tr>";
      }
      html += "</tbody></table></div>";
      blocos.push(html);
      continue;
    }

    if (/^\s*>\s?/.test(linha)) {
      const partes = [];
      while (i < linhas.length && /^\s*>\s?/.test(linhas[i])) {
        partes.push(linhas[i].replace(/^\s*>\s?/, ""));
        i++;
      }
      blocos.push(`<blockquote>${inline(partes.join(" "))}</blockquote>`);
      continue;
    }

    const itemLista = linha.match(/^\s*([-*+]|\d+\.)\s+(.*)$/);
    if (itemLista) {
      const ordenada = /\d+\./.test(itemLista[1]);
      const itens = [];
      while (i < linhas.length) {
        const achado = linhas[i].match(/^\s*([-*+]|\d+\.)\s+(.*)$/);
        if (!achado) break;
        itens.push(achado[2]);
        i++;
      }
      const tag = ordenada ? "ol" : "ul";
      blocos.push(
        `<${tag}>${itens.map((item) => `<li>${inline(item)}</li>`).join("")}</${tag}>`
      );
      continue;
    }

    const paragrafo = [];
    while (i < linhas.length) {
      const atual = linhas[i];
      if (!atual.trim()) break;
      if (/^#{1,4}\s+/.test(atual)) break;
      if (atual.trim().startsWith("```")) break;
      if (/^\s*>\s?/.test(atual)) break;
      if (/^\s*([-*+]|\d+\.)\s+/.test(atual)) break;
      if (/^\s*(?:-{3,}|\*{3,}|_{3,})\s*$/.test(atual)) break;
      if (
        atual.includes("|") &&
        i + 1 < linhas.length &&
        ehSeparadorTabela(linhas[i + 1])
      ) {
        break;
      }
      paragrafo.push(atual);
      i++;
    }
    if (paragrafo.length) {
      blocos.push(`<p>${inline(paragrafo.join("<br>"))}</p>`);
    } else {
      i++;
    }
  }

  return blocos.join("");
}

function estadoInicial() {
  const hoje = new Date();
  return {
    conversas: [],
    ativa: null,
    gastos: [],
    memorias: [],
    mes: hoje.getMonth() + 1,
    ano: hoje.getFullYear(),
  };
}

function hojeISO() {
  return new Date().toLocaleDateString("en-CA", {
    timeZone: "America/Sao_Paulo",
  });
}

function normalizarGastos(lista) {
  if (!Array.isArray(lista)) return [];
  return lista
    .filter((gasto) => gasto && typeof gasto === "object")
    .map((gasto) => ({
      id: Number(gasto.id) || 0,
      descricao: String(gasto.descricao || "Despesa").slice(0, 120),
      valor: arredondar(gasto.valor || 0),
      categoria: CATEGORIAS.includes(gasto.categoria)
        ? gasto.categoria
        : "Outros",
      data: /^\d{4}-\d{2}-\d{2}$/.test(String(gasto.data || ""))
        ? String(gasto.data)
        : hojeISO(),
    }));
}

function normalizarMemorias(lista) {
  if (!Array.isArray(lista)) return [];
  return lista
    .filter((memoria) => memoria && typeof memoria === "object")
    .map((memoria) => ({
      id: Number(memoria.id) || 0,
      conteudo: String(memoria.conteudo || "").slice(0, 500),
    }))
    .filter((memoria) => memoria.conteudo);
}

function normalizarConversa(item) {
  if (!item || typeof item !== "object") return null;
  const mensagens = (Array.isArray(item.mensagens) ? item.mensagens : [])
    .filter(
      (mensagem) =>
        mensagem &&
        (mensagem.role === "user" || mensagem.role === "assistant") &&
        typeof mensagem.content === "string"
    )
    .map((mensagem) => ({
      role: mensagem.role,
      content: mensagem.content.slice(0, 8000),
    }))
    .slice(-LIMITE_MENSAGENS);
  return {
    id:
      typeof item.id === "string" && item.id.length > 0 ? item.id : novoId(),
    titulo: typeof item.titulo === "string" ? item.titulo.slice(0, 80) : "",
    criado_em:
      typeof item.criado_em === "string"
        ? item.criado_em
        : new Date().toISOString(),
    atualizado_em:
      typeof item.atualizado_em === "string"
        ? item.atualizado_em
        : new Date().toISOString(),
    mensagens,
  };
}

function carregarEstado() {
  const base = estadoInicial();
  try {
    const bruto = JSON.parse(localStorage.getItem(CHAVE_ESTADO) || "null");
    if (!bruto || typeof bruto !== "object") return base;
    const conversas = (Array.isArray(bruto.conversas) ? bruto.conversas : [])
      .map(normalizarConversa)
      .filter(Boolean);
    const ids = new Set(conversas.map((conversa) => conversa.id));
    return {
      conversas,
      ativa: ids.has(bruto.ativa) ? bruto.ativa : conversas[0]?.id || null,
      gastos: normalizarGastos(bruto.gastos),
      memorias: normalizarMemorias(bruto.memorias),
      mes:
        Number(bruto.mes) >= 1 && Number(bruto.mes) <= 12
          ? Number(bruto.mes)
          : base.mes,
      ano: Number(bruto.ano) >= 2000 ? Number(bruto.ano) : base.ano,
    };
  } catch (erro) {
    return base;
  }
}

const estado = carregarEstado();

function salvarEstado() {
  estado.conversas.sort(
    (a, b) => new Date(b.atualizado_em) - new Date(a.atualizado_em)
  );
  while (estado.conversas.length > LIMITE_CONVERSAS) {
    estado.conversas.pop();
  }
  let serializado = JSON.stringify(estado);
  while (serializado.length > 4000000 && estado.conversas.length > 1) {
    const indice = estado.conversas.findIndex(
      (conversa) => conversa.id !== estado.ativa
    );
    if (indice < 0) break;
    estado.conversas.splice(indice, 1);
    serializado = JSON.stringify(estado);
  }
  try {
    localStorage.setItem(CHAVE_ESTADO, serializado);
  } catch (erro) {
    aviso("Não foi possível salvar o histórico neste navegador.");
  }
}

function conversaAtiva() {
  return estado.conversas.find((conversa) => conversa.id === estado.ativa);
}

function criarConversa() {
  const agora = new Date().toISOString();
  const nova = {
    id: novoId(),
    titulo: "",
    criado_em: agora,
    atualizado_em: agora,
    mensagens: [],
  };
  estado.conversas.unshift(nova);
  estado.ativa = nova.id;
  salvarEstado();
  return nova;
}

function garantirConversa() {
  if (!estado.conversas.length) {
    criarConversa();
    return;
  }
  if (!conversaAtiva()) {
    estado.ativa = estado.conversas[0].id;
  }
}

function aviso(texto) {
  avisoEl.textContent = texto;
  avisoEl.classList.add("visivel");
  if (timerAviso) clearTimeout(timerAviso);
  timerAviso = setTimeout(() => {
    avisoEl.classList.remove("visivel");
  }, 2600);
}

function rolarParaFim(imediato) {
  const destino = conteudo.scrollHeight;
  if (imediato) {
    conteudo.scrollTop = destino;
  } else {
    conteudo.scrollTo({ top: destino, behavior: "smooth" });
  }
}

function formatarDataCurta(iso) {
  const partes = String(iso).split("-");
  if (partes.length !== 3) return "";
  return `${partes[2]}/${partes[1]}`;
}

function preencherSelects() {
  mesEl.innerHTML = "";
  MESES.forEach((nome, indice) => {
    const opcao = document.createElement("option");
    opcao.value = String(indice + 1);
    opcao.textContent = nome;
    mesEl.appendChild(opcao);
  });

  const anoAtual = new Date().getFullYear();
  const anos = [anoAtual - 2, anoAtual - 1, anoAtual, anoAtual + 1];
  if (!anos.includes(estado.ano)) estado.ano = anoAtual;
  anoEl.innerHTML = "";
  anos.forEach((ano) => {
    const opcao = document.createElement("option");
    opcao.value = String(ano);
    opcao.textContent = String(ano);
    anoEl.appendChild(opcao);
  });

  mesEl.value = String(estado.mes);
  anoEl.value = String(estado.ano);
}

function renderHistorico() {
  historicoEl.innerHTML = "";
  const visiveis = estado.conversas.filter(
    (conversa) =>
      conversa.mensagens.length > 0 || conversa.id === estado.ativa
  );

  if (!visiveis.length) {
    const vazio = document.createElement("div");
    vazio.className = "historico-vazio";
    vazio.textContent = "Nenhuma conversa ainda.";
    historicoEl.appendChild(vazio);
    return;
  }

  for (const conversa of visiveis) {
    const botao = document.createElement("button");
    botao.type = "button";
    botao.className =
      "item-historico" + (conversa.id === estado.ativa ? " ativo" : "");
    botao.dataset.id = conversa.id;
    botao.textContent = conversa.titulo || "Nova conversa";
    botao.title = conversa.titulo || "Nova conversa";
    historicoEl.appendChild(botao);
  }
}

function resumoMes() {
  const gastos = estado.gastos
    .filter((gasto) => {
      const partes = String(gasto.data).split("-").map(Number);
      return partes[1] === estado.mes && partes[0] === estado.ano;
    })
    .sort((a, b) => b.data.localeCompare(a.data) || b.id - a.id);

  const porCategoria = new Map();
  let total = 0;
  for (const gasto of gastos) {
    total += gasto.valor;
    porCategoria.set(
      gasto.categoria,
      (porCategoria.get(gasto.categoria) || 0) + gasto.valor
    );
  }

  const categorias = [...porCategoria.entries()]
    .map(([nome, valor]) => [nome, arredondar(valor)])
    .sort((a, b) => b[1] - a[1]);

  return {
    gastos,
    total: arredondar(total),
    quantidade: gastos.length,
    categorias,
  };
}

function renderCards(resumo) {
  cardsEl.innerHTML = "";
  const itens = [
    ["Total do mês", moeda.format(resumo.total)],
    ["Lançamentos", String(resumo.quantidade)],
    [
      "Maior categoria",
      resumo.categorias.length ? resumo.categorias[0][0] : "Sem lançamentos",
    ],
  ];

  for (const [rotulo, valor] of itens) {
    const card = document.createElement("div");
    card.className = "card";
    const titulo = document.createElement("span");
    titulo.textContent = rotulo;
    const forte = document.createElement("strong");
    forte.textContent = valor;
    forte.title = valor;
    card.append(titulo, forte);
    cardsEl.appendChild(card);
  }
}

function renderTabela(resumo) {
  tabelaEl.innerHTML = "";

  if (!resumo.gastos.length) {
    const vazio = document.createElement("div");
    vazio.className = "tabela-vazia";
    vazio.textContent = "Nenhum lançamento neste mês.";
    tabelaEl.appendChild(vazio);
    return;
  }

  const envolucro = document.createElement("div");
  envolucro.className = "tabela-rolagem";
  const tabela = document.createElement("table");
  tabela.className = "tabela-painel";

  const cabecalho = document.createElement("thead");
  const linhaCabecalho = document.createElement("tr");
  for (const titulo of ["Data", "Descrição", "Categoria", "Valor"]) {
    const celula = document.createElement("th");
    celula.textContent = titulo;
    if (titulo === "Valor") celula.className = "valor";
    linhaCabecalho.appendChild(celula);
  }
  cabecalho.appendChild(linhaCabecalho);

  const corpo = document.createElement("tbody");
  for (const gasto of resumo.gastos) {
    const linha = document.createElement("tr");
    const dados = [
      formatarDataCurta(gasto.data),
      gasto.descricao,
      gasto.categoria,
      moeda.format(gasto.valor),
    ];
    dados.forEach((valor, indice) => {
      const celula = document.createElement("td");
      celula.textContent = valor;
      if (indice === 1) celula.title = valor;
      if (indice === 3) celula.className = "valor";
      linha.appendChild(celula);
    });
    corpo.appendChild(linha);
  }

  tabela.append(cabecalho, corpo);
  envolucro.appendChild(tabela);
  tabelaEl.appendChild(envolucro);
}

function renderMemorias() {
  memoriaEl.innerHTML = "";

  if (!estado.memorias.length) {
    const vazio = document.createElement("p");
    vazio.className = "memoria-vazia";
    vazio.textContent = "Nenhuma memória registrada.";
    memoriaEl.appendChild(vazio);
    return;
  }

  const lista = document.createElement("ul");
  for (const memoria of estado.memorias) {
    const item = document.createElement("li");
    item.textContent = memoria.conteudo;
    lista.appendChild(item);
  }
  memoriaEl.appendChild(lista);
}

function renderPainel() {
  const resumo = resumoMes();
  renderCards(resumo);
  renderTabela(resumo);
  renderMemorias();
}

function adicionarBolha(role, texto) {
  const artigo = document.createElement("article");
  artigo.className =
    "mensagem " + (role === "user" ? "usuario" : "assistente");
  const corpo = document.createElement("div");
  corpo.className = "markdown";
  corpo.innerHTML = markdown(texto);
  artigo.appendChild(corpo);
  conversaEl.appendChild(artigo);
  return artigo;
}

function renderConversa() {
  conversaEl.innerHTML = "";
  const ativa = conversaAtiva();
  const mensagens = ativa ? ativa.mensagens : [];

  if (!mensagens.length) {
    adicionarBolha("assistant", BEM_VINDO);
  } else {
    for (const mensagem of mensagens) {
      adicionarBolha(mensagem.role, mensagem.content);
    }
  }

  rolarParaFim(true);
}

function renderTudo() {
  garantirConversa();
  renderHistorico();
  renderPainel();
  renderConversa();
  mesEl.value = String(estado.mes);
  anoEl.value = String(estado.ano);
}

function definirOcupado(ocupado) {
  enviando = ocupado;
  campo.disabled = ocupado;
  enviarBtn.disabled = ocupado;
  if (!ocupado) focarCampo();
}

function focarCampo() {
  if (window.matchMedia("(pointer: fine)").matches) {
    campo.focus();
  }
}

function ajustarAltura() {
  campo.style.height = "auto";
  campo.style.height = Math.min(campo.scrollHeight, 160) + "px";
}

function abrirMenu() {
  app.classList.add("menu-aberto");
  abrirMenuBtn.setAttribute("aria-expanded", "true");
}

function fecharMenu() {
  app.classList.remove("menu-aberto");
  abrirMenuBtn.setAttribute("aria-expanded", "false");
}

async function enviar(texto) {
  const ativa = conversaAtiva();
  if (!ativa || enviando) return;

  const idConversa = ativa.id;
  const primeira = ativa.mensagens.length === 0;

  ativa.mensagens.push({ role: "user", content: texto });
  if (primeira) {
    ativa.titulo = texto.replace(/\s+/g, " ").trim().slice(0, 48);
  }
  ativa.atualizado_em = new Date().toISOString();
  salvarEstado();
  renderTudo();
  fecharMenu();

  const bolha = adicionarBolha("assistant", "");
  bolha.innerHTML =
    '<div class="status"><span class="digitando"><i></i><i></i><i></i></span>' +
    "<span>Analisando a solicitação...</span></div>";
  rolarParaFim(true);
  definirOcupado(true);

  try {
    const resposta = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mensagens: ativa.mensagens.slice(-40),
        estado: { gastos: estado.gastos, memorias: estado.memorias },
      }),
    });

    let dados = {};
    try {
      dados = await resposta.json();
    } catch (erro) {
      dados = {};
    }

    if (dados.estado) {
      if (Array.isArray(dados.estado.gastos)) {
        estado.gastos = normalizarGastos(dados.estado.gastos);
      }
      if (Array.isArray(dados.estado.memorias)) {
        estado.memorias = normalizarMemorias(dados.estado.memorias);
      }
    }

    if (!resposta.ok) {
      throw new Error(
        dados.erro || `Não foi possível concluir a solicitação (${resposta.status}).`
      );
    }

    const conteudo =
      String(dados.resposta || "").trim() ||
      "Não foi possível concluir a solicitação. Tente novamente.";

    const conversa = estado.conversas.find(
      (item) => item.id === idConversa
    );
    if (conversa) {
      conversa.mensagens.push({ role: "assistant", content: conteudo });
      conversa.atualizado_em = new Date().toISOString();
    }
    salvarEstado();

    if (estado.ativa === idConversa) {
      renderTudo();
      rolarParaFim();
    } else {
      renderHistorico();
      renderPainel();
      aviso("Resposta adicionada à conversa anterior.");
    }
  } catch (erro) {
    const mensagem = erro.message || "Falha na conexão com o servidor.";
    if (estado.ativa === idConversa) {
      bolha.classList.add("falha");
      bolha.innerHTML = `<div class="markdown"><p>${escaparHtml(mensagem)}</p></div>`;
      rolarParaFim();
    } else {
      aviso(mensagem);
    }
  } finally {
    definirOcupado(false);
  }
}

formulario.addEventListener("submit", (evento) => {
  evento.preventDefault();
  if (enviando) return;
  const texto = campo.value.trim();
  if (!texto) return;
  campo.value = "";
  ajustarAltura();
  enviar(texto);
});

campo.addEventListener("keydown", (evento) => {
  if (evento.key === "Enter" && !evento.shiftKey && !evento.isComposing) {
    evento.preventDefault();
    formulario.requestSubmit();
  }
});

campo.addEventListener("input", ajustarAltura);

historicoEl.addEventListener("click", (evento) => {
  const alvo = evento.target.closest(".item-historico");
  if (!alvo) return;
  estado.ativa = alvo.dataset.id;
  salvarEstado();
  renderTudo();
  fecharMenu();
});

document.getElementById("nova-conversa").addEventListener("click", () => {
  const vazia = estado.conversas.find(
    (conversa) => conversa.mensagens.length === 0
  );
  if (vazia) {
    estado.ativa = vazia.id;
    salvarEstado();
    renderTudo();
    aviso("Você já está em uma conversa nova.");
  } else {
    criarConversa();
    renderTudo();
  }
  fecharMenu();
  focarCampo();
});

document.getElementById("excluir-conversa").addEventListener("click", () => {
  const ativa = conversaAtiva();
  if (!ativa) return;
  estado.conversas = estado.conversas.filter(
    (conversa) => conversa.id !== ativa.id
  );
  estado.ativa = estado.conversas.length ? estado.conversas[0].id : null;
  if (!estado.conversas.length) criarConversa();
  salvarEstado();
  renderTudo();
  fecharMenu();
  aviso("Conversa excluída.");
});

document.getElementById("limpar-memorias").addEventListener("click", () => {
  if (!estado.memorias.length) {
    aviso("Nenhuma memória registrada.");
    return;
  }
  estado.memorias = [];
  salvarEstado();
  renderPainel();
  aviso("Memórias removidas.");
});

mesEl.addEventListener("change", () => {
  estado.mes = Number(mesEl.value);
  salvarEstado();
  renderPainel();
});

anoEl.addEventListener("change", () => {
  estado.ano = Number(anoEl.value);
  salvarEstado();
  renderPainel();
});

abrirMenuBtn.addEventListener("click", () => {
  if (app.classList.contains("menu-aberto")) {
    fecharMenu();
  } else {
    abrirMenu();
  }
});

document.querySelectorAll("[data-fechar-menu]").forEach((elemento) => {
  elemento.addEventListener("click", fecharMenu);
});

document.addEventListener("keydown", (evento) => {
  if (evento.key === "Escape") fecharMenu();
});

window.addEventListener("resize", () => {
  if (window.innerWidth > 900) fecharMenu();
});

preencherSelects();
garantirConversa();
renderTudo();
ajustarAltura();
focarCampo();
