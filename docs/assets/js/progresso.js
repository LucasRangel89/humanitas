// Humanitas — progresso das trilhas marcado no navegador.
//
// O site é estático: este script não escreve no repositório. Ele:
//   1. transforma as caixas (somente leitura) das trilhas em caixas clicáveis;
//   2. guarda a marcação em localStorage (por navegador);
//   3. mostra o progresso da trilha no topo da página;
//   4. exporta/importa um progresso.json, que o CLI converte em commit:
//        make aplicar-progresso ARQUIVO=progresso.json
document.addEventListener('DOMContentLoaded', () => {
  const lista = document.querySelector('.md-content .task-list');
  if (!lista || !location.pathname.includes('/trilhas/')) return;

  const CHAVE = 'humanitas.progresso.v1';
  const trilhaId = location.pathname.replace(/\/+$/, '').split('/').pop();

  const lerTudo = () => {
    try {
      const dados = JSON.parse(localStorage.getItem(CHAVE) || '{}');
      if (!dados.trilhas) dados.trilhas = {};
      return dados;
    } catch {
      return { trilhas: {} };
    }
  };

  const gravarTudo = (dados) => {
    dados.versao = 1;
    dados.atualizado_em = new Date().toISOString();
    localStorage.setItem(CHAVE, JSON.stringify(dados));
  };

  const dados = lerTudo();
  const marcados = new Set(dados.trilhas[trilhaId] || []);
  const itens = [...lista.querySelectorAll('li.task-list-item')];
  if (!itens.length) return;

  // ---- painel de progresso -------------------------------------------------
  const painel = document.createElement('div');
  painel.className = 'hum-painel';
  painel.innerHTML = `
    <div class="hum-painel-topo">
      <strong>Progresso desta trilha</strong>
      <span id="hum-contagem"></span>
    </div>
    <div class="hum-barra"><span id="hum-barra-preenchida"></span></div>
    <div class="hum-acoes">
      <button type="button" class="hum-btn" data-acao="exportar">Exportar progresso</button>
      <button type="button" class="hum-btn" data-acao="importar">Importar…</button>
      <input type="file" id="hum-arquivo" accept="application/json" hidden>
      <button type="button" class="hum-btn hum-btn-sutil" data-acao="limpar">Limpar</button>
    </div>
    <p class="hum-nota">A marcação fica <strong>neste navegador</strong>. Para gravar no repositório:
      exporte e rode <code>make aplicar-progresso ARQUIVO=progresso.json</code>.</p>
  `;
  lista.parentElement.insertBefore(painel, lista);

  const contagem = painel.querySelector('#hum-contagem');
  const preenchida = painel.querySelector('#hum-barra-preenchida');

  function atualizarPainel() {
    const total = itens.length;
    const feitos = itens.filter((li) => li.querySelector('input')?.checked).length;
    const pct = total ? Math.round((feitos * 100) / total) : 0;
    contagem.textContent = `${feitos}/${total} · ${pct}%`;
    preenchida.style.width = `${pct}%`;
    preenchida.parentElement.setAttribute('aria-valuenow', String(pct));
  }

  function sincronizarDados() {
    const checados = itens
      .map((li, i) => (li.querySelector('input')?.checked ? i : -1))
      .filter((i) => i >= 0);
    const tudo = lerTudo();
    if (checados.length) tudo.trilhas[trilhaId] = checados;
    else delete tudo.trilhas[trilhaId];
    gravarTudo(tudo);
  }

  // ---- caixas clicáveis ----------------------------------------------------
  itens.forEach((li, i) => {
    const input = li.querySelector('input[type="checkbox"]');
    if (!input) return;
    input.disabled = false;
    input.checked = marcados.has(i);
    li.classList.toggle('hum-feito', input.checked);
    input.setAttribute('aria-label', `Marcar o nó ${i + 1} como concluído`);
    input.addEventListener('change', () => {
      li.classList.toggle('hum-feito', input.checked);
      sincronizarDados();
      atualizarPainel();
    });
  });
  atualizarPainel();

  // ---- exportar / importar / limpar ---------------------------------------
  const baixar = (nome, texto) => {
    const blob = new Blob([texto], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  painel.querySelector('[data-acao="exportar"]').addEventListener('click', () => {
    const tudo = lerTudo();
    const saida = {
      versao: 1,
      exportado_em: new Date().toISOString(),
      trilhas: tudo.trilhas,
    };
    baixar('progresso.json', JSON.stringify(saida, null, 2));
  });

  const arquivo = painel.querySelector('#hum-arquivo');
  painel.querySelector('[data-acao="importar"]').addEventListener('click', () => arquivo.click());
  arquivo.addEventListener('change', () => {
    const f = arquivo.files?.[0];
    if (!f) return;
    const leitor = new FileReader();
    leitor.onload = () => {
      try {
        const importado = JSON.parse(String(leitor.result));
        const tudo = lerTudo();
        Object.entries(importado.trilhas || {}).forEach(([slug, indices]) => {
          tudo.trilhas[slug] = indices;
        });
        gravarTudo(tudo);
        if (trilhaId in (importado.trilhas || {})) {
          location.reload();
        }
      } catch {
        alert('Arquivo inválido: esperado o progresso.json exportado pelo site.');
      }
    };
    leitor.readAsText(f);
  });

  painel.querySelector('[data-acao="limpar"]').addEventListener('click', () => {
    if (!confirm('Limpar a marcação local desta trilha? (o repositório não é afetado)')) return;
    const tudo = lerTudo();
    delete tudo.trilhas[trilhaId];
    gravarTudo(tudo);
    itens.forEach((li) => {
      const input = li.querySelector('input');
      if (input) input.checked = false;
      li.classList.remove('hum-feito');
    });
    atualizarPainel();
  });
});
