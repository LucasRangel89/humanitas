// Humanitas — página "Registrar": monta a nota e leva ao GitHub preenchido.
document.addEventListener('DOMContentLoaded', () => {
  const cfgEl = document.getElementById('hum-config');
  const form = document.getElementById('hum-criar');
  if (!cfgEl || !form) return;

  const cfg = JSON.parse(cfgEl.textContent);
  const $ = (id) => document.getElementById(id);
  const tipo = $('hum-tipo');
  const nome = $('hum-nome');
  const tema = $('hum-tema');
  const nivel = $('hum-nivel');
  const autor = $('hum-autor');
  const obra = $('hum-obra');
  const ano = $('hum-ano');
  const capitulo = $('hum-capitulo');
  const pagina = $('hum-pagina');
  const saida = $('hum-saida');
  const caminho = $('hum-caminho');
  const github = $('hum-github');
  const dica = $('hum-dica');

  // Select de temas (nome legível, valor = slug)
  Object.entries(cfg.temas)
    .sort((a, b) => a[1].localeCompare(b[1], 'pt-BR'))
    .forEach(([slugValor, rotulo]) => {
      const op = document.createElement('option');
      op.value = slugValor;
      op.textContent = rotulo;
      tema.appendChild(op);
    });
  tema.value = cfg.temas.sociologia ? 'sociologia' : tema.options[0].value;

  function slug(texto) {
    return (texto || '')
      .normalize('NFKD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '')
      .replace(/-+/g, '-');
  }

  function esc(txt) {
    return (txt || '').replace(/"/g, '\\"');
  }

  function camposExtras() {
    const t = tipo.value;
    $('hum-campo-ano').hidden = t !== 'ficha';
    $('hum-campo-cap').hidden = t !== 'trecho';
    $('hum-campo-pag').hidden = t !== 'trecho';
  }

  function frontmatter(dados) {
    return ['---', ...Object.entries(dados).map(([k, v]) => `${k}: ${v}`), '---', ''].join('\n');
  }

  function corpoConceito(n) {
    return `# Conceito — ${n}

## Definição em uma frase

A definição mais enxuta possível, capaz de caber em um cartão de memória.

## Explicação com as minhas palavras

Explique o conceito em 3 a 5 frases, como se ensinasse a alguém. Use um exemplo brasileiro concreto (do seu bairro, trabalho, família ou de uma notícia).

## Onde aparece na obra

Capítulo ou seção onde o autor apresenta o conceito, e o que ele destaca nele.

## Trecho de apoio

> "Citação literal curta do autor, com capítulo (e página se houver)."

Uma frase explicando por que este trecho captura bem o conceito.

## Exemplos que ilustram

- Exemplo 1: ...

## Conceitos relacionados

- [Conceito vizinho](arquivo-do-conceito-vizinho.md) — por que ele completa ou contrasta este.

## Conexões interdisciplinares

- **Outro tema — nota:** por que a conexão existe (não basta citar o nome).

## Por que este conceito importa

Uma frase sobre a consequência de entender (ou ignorar) este conceito.
`;
  }

  function corpoEixo(n) {
    return `# Eixo — ${n}

## A questão em uma frase

Formule o debate como uma pergunta que não tem resposta única.

## Por que é uma grande questão

3 a 5 frases: o que está em jogo e o que muda na vida real conforme a resposta.

## Posições no debate

| Posição | Autores | Obra de referência | Nota no painel |
|---|---|---|---|
| Posição A | ... | ... | ... |
| Posição B | ... | ... | ... |

## Como usar este eixo (a pergunta-bússola)

Ao estudar qualquer teoria nova, pergunte: "onde ela fica neste eixo?" — e registre aqui.

## Conexões interdisciplinares

- **Tema — ângulo:** uma frase.
`;
  }

  function corpoTrecho(n) {
    return `# Trecho — ${n}

## O trecho

> "Cole aqui a citação literal."

## Por que guardei este trecho

O que ele muda na sua compreensão — em duas ou três frases.
`;
  }

  function corpoDiario(n) {
    return `# Diário — ${n}

## A pergunta reflexiva

A pergunta que a sessão de estudo deixou (do Tutor ou sua).

## Minha síntese

100 a 150 palavras, com as suas palavras. Sem IA.

## O que ainda não entendi

Lacunas honestas — elas viram os próximos nós.

## Próximo passo de estudo

Uma frase.
`;
  }

  function corpoFicha(n) {
    return `# Ficha de leitura — ${n}

## Identificação

- **Obra:** ${obra.value || n}
- **Autor:** ${autor.value || ''}
- **Ano de publicação:** ${ano.value || ''}
- **Por que escolhi este livro:**

## O problema do autor

Qual pergunta o autor tenta responder? (1 a 2 frases.)

## Tese central

O argumento principal em no máximo 3 frases.

## Resumo por capítulos

Para cada capítulo, 3 a 5 frases.

## Conceitos-chave

- 

## Perguntas que ficaram

- 
`;
  }

  function montar() {
    camposExtras();
    const t = tipo.value;
    const n = nome.value.trim() || 'Nome do conceito';
    const s = slug(nome.value) || 'nome-novo';
    const temaValor = tema.value;
    const nivelValor = nivel.value;
    const tagsExtras = t === 'eixo' ? '[eixo, ' + temaValor + ']' : '[' + temaValor + ']';

    let fm = {};
    let corpo = '';
    let pasta = cfg.pastas[t] || 'conceitos';
    let arquivo = `${s}.md`;

    if (t === 'conceito') {
      fm = {
        conceito: `"${esc(n)}"`,
        obra_origem: `"${esc(obra.value)}"`,
        autor_origem: `"${esc(autor.value)}"`,
        tema: temaValor,
        tipo: 'conceito',
        nivel: nivelValor,
        status: 'rascunho',
        fonte_verificada: 'nao',
        eixos: '[]',
        relacoes: '[]',
        tags: tagsExtras,
      };
      arquivo = `${temaValor}-${s}.md`;
      corpo = corpoConceito(n);
    } else if (t === 'eixo') {
      fm = {
        eixo: `"${esc(n)}"`,
        tema: temaValor,
        tipo: 'eixo',
        nivel: nivelValor,
        status: 'rascunho',
        fonte_verificada: 'nao',
        eixos: '[]',
        relacoes: '[]',
        tags: tagsExtras,
      };
      arquivo = `eixo-${s}.md`;
      corpo = corpoEixo(n);
    } else if (t === 'trecho') {
      fm = {
        obra: `"${esc(obra.value || n)}"`,
        autor: `"${esc(autor.value)}"`,
        capitulo: `"${esc(capitulo.value)}"`,
        pagina: `"${esc(pagina.value)}"`,
        tema: temaValor,
        tipo: 'trecho',
        tags: tagsExtras,
      };
      corpo = corpoTrecho(n);
    } else if (t === 'diario') {
      fm = {
        data: cfg.hoje,
        tema: temaValor,
        origem: `"${esc(n)}"`,
        tipo: 'diario',
        tags: '[diario, ' + temaValor + ']',
      };
      arquivo = `${cfg.hoje}-${temaValor}-${s}.md`;
      corpo = corpoDiario(n);
    } else {
      fm = {
        obra: `"${esc(obra.value || n)}"`,
        autor: `"${esc(autor.value)}"`,
        ano: `"${esc(ano.value)}"`,
        tema: temaValor,
        tipo: 'ficha-de-leitura',
        status: 'em-andamento',
        tags: tagsExtras,
      };
      arquivo = `${s}-ficha.md`;
      corpo = corpoFicha(n);
    }

    const conteudo = frontmatter(fm) + corpo;
    saida.value = conteudo;
    const destino = `${pasta}/${arquivo}`;
    caminho.textContent = destino;

    // GitHub: /new/<branch>/<pasta>?filename=<arquivo>&value=<conteudo>
    const url = `${cfg.repo}/new/main/${pasta}?filename=${encodeURIComponent(arquivo)}&value=${encodeURIComponent(conteudo)}`;
    if (url.length > 7000) {
      github.removeAttribute('href');
      github.classList.add('hum-btn-off');
      dica.textContent = 'Conteúdo longo demais para a URL do GitHub — use "Copiar Markdown".';
    } else {
      github.href = url;
      github.classList.remove('hum-btn-off');
      dica.textContent = '';
    }
    return destino;
  }

  form.addEventListener('input', montar);
  form.addEventListener('change', montar);
  montar();

  document.querySelectorAll('[data-acao="copiar"]').forEach((btn) => {
    btn.addEventListener('click', async () => {
      try {
        await navigator.clipboard.writeText(saida.value);
        btn.textContent = 'Copiado ✓';
        setTimeout(() => { btn.textContent = 'Copiar Markdown'; }, 1800);
      } catch {
        saida.removeAttribute('readonly');
        saida.select();
        document.execCommand('copy');
        saida.setAttribute('readonly', 'readonly');
      }
    });
  });
});
