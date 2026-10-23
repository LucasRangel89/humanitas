// Humanitas — progresso das trilhas marcado no navegador.
//
// O site é estático: este script não escreve no repositório. Ele:
//   1. nas páginas de trilha, transforma as caixas (somente leitura) em clicáveis;
//   2. guarda a marcação em localStorage (por navegador);
//   3. na página "Registrar", mostra a central do progresso de todas as trilhas;
//   4. exporta/importa um progresso.json, que o CLI converte em commit:
//        make aplicar-progresso ARQUIVO=progresso.json
(() => {
  const CHAVE = 'humanitas.progresso.v1';
  const COMANDO = 'make aplicar-progresso ARQUIVO=~/Downloads/progresso.json';

  // ---- armazenamento -------------------------------------------------------
  const lerTudo = () => {
    try {
      const dados = JSON.parse(localStorage.getItem(CHAVE) || '{}');
      if (!dados.trilhas || typeof dados.trilhas !== 'object') dados.trilhas = {};
      return dados;
    } catch {
      return { trilhas: {} };
    }
  };

  const gravarTudo = (dados) => {
    dados.versao = 1;
    dados.atualizado_em = new Date().toISOString();
    try {
      localStorage.setItem(CHAVE, JSON.stringify(dados));
      return true;
    } catch {
      avisar('Não consegui salvar neste navegador (armazenamento cheio ou bloqueado).');
      return false;
    }
  };

  const marcadosDe = (tudo, slug) =>
    (tudo.trilhas[slug] || []).filter((i) => Number.isInteger(i) && i >= 0);

  // ---- utilidades de tela --------------------------------------------------
  let destinoAviso = null;
  const avisar = (texto) => {
    if (destinoAviso) destinoAviso.textContent = texto;
  };

  const baixar = (nome, texto, tipo) => {
    const blob = new Blob([texto], { type: tipo || 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = nome;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const copiar = async (texto) => {
    try {
      await navigator.clipboard.writeText(texto);
      return true;
    } catch {
      const area = document.createElement('textarea');
      area.value = texto;
      document.body.appendChild(area);
      area.select();
      const ok = document.execCommand('copy');
      area.remove();
      return ok;
    }
  };

  const dadosExportaveis = (tudo) => ({
    versao: 1,
    exportado_em: new Date().toISOString(),
    trilhas: tudo.trilhas,
  });

  const exportarJson = () => {
    const tudo = lerTudo();
    baixar('progresso.json', JSON.stringify(dadosExportaveis(tudo), null, 2));
    avisar('progresso.json baixado. Guarde como backup e use "Importar…" para restaurar.');
  };

  const importarArquivo = (input, aoImportar) => {
    const f = input.files && input.files[0];
    if (!f) return;
    const leitor = new FileReader();
    leitor.onload = () => {
      let importado;
      try {
        importado = JSON.parse(String(leitor.result));
      } catch {
        alert('Arquivo inválido: esperado o progresso.json exportado pelo site.');
        return;
      }
      const trilhas = importado && importado.trilhas;
      if (!trilhas || typeof trilhas !== 'object') {
        alert('Arquivo inválido: falta a chave "trilhas".');
        return;
      }
      const tudo = lerTudo();
      let quantas = 0;
      Object.entries(trilhas).forEach(([slug, indices]) => {
        if (!Array.isArray(indices)) return;
        tudo.trilhas[slug] = indices
          .map((i) => Number(i))
          .filter((i) => Number.isInteger(i) && i >= 0);
        quantas += 1;
      });
      if (!quantas) {
        alert('Nada para importar: o arquivo não tem trilhas válidas.');
        return;
      }
      gravarTudo(tudo);
      if (aoImportar) aoImportar(quantas);
    };
    leitor.readAsText(f);
    input.value = ''; // permite reimportar o mesmo arquivo
  };

  // ---- página de trilha ----------------------------------------------------
  function iniciarTrilha() {
    const lista = document.querySelector('.md-content .task-list');
    if (!lista || !location.pathname.includes('/trilhas/')) return;

    const trilhaId = location.pathname.replace(/\/+$/, '').split('/').pop();
    const itens = [...lista.querySelectorAll('li.task-list-item')];
    if (!itens.length) return;

    const tudo = lerTudo();
    const marcados = new Set(marcadosDe(tudo, trilhaId));

    // ---- painel de progresso ----------------------------------------------
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
        <input type="file" class="hum-input-arquivo" accept="application/json" hidden>
        <button type="button" class="hum-btn hum-btn-sutil" data-acao="copiar-comando">Copiar comando</button>
        <button type="button" class="hum-btn hum-btn-sutil" data-acao="limpar">Limpar</button>
      </div>
      <p class="hum-nota">A marcação fica <strong>neste navegador</strong>. Para gravar no repositório:
        exporte e rode <code>${COMANDO}</code>.</p>
      <p class="hum-nota">Backup e importação de todas as trilhas: <a href="../../registrar/#hum-progresso">central de progresso</a>.</p>
      <p class="hum-dica" data-aviso></p>
    `;
    lista.parentElement.insertBefore(painel, lista);
    destinoAviso = painel.querySelector('[data-aviso]');

    const contagem = painel.querySelector('#hum-contagem');
    const preenchida = painel.querySelector('#hum-barra-preenchida');

    const atualizarPainel = () => {
      const total = itens.length;
      const feitos = itens.filter((li) => li.querySelector('input') && li.querySelector('input').checked).length;
      const pct = total ? Math.round((feitos * 100) / total) : 0;
      contagem.textContent = `${feitos}/${total} · ${pct}%`;
      preenchida.style.width = `${pct}%`;
      preenchida.parentElement.setAttribute('aria-valuenow', String(pct));

      if (feitos === total && total > 0) {
        avisar('Trilha completa: "make aplicar-progresso" marca o status como concluida.');
      } else if (feitos > 0) {
        avisar(`${total - feitos} nó(s) para fechar a trilha.`);
      } else {
        avisar('');
      }
    };

    const sincronizarDados = () => {
      const checados = itens
        .map((li, i) => (li.querySelector('input') && li.querySelector('input').checked ? i : -1))
        .filter((i) => i >= 0);
      const agora = lerTudo();
      if (checados.length) agora.trilhas[trilhaId] = checados;
      else delete agora.trilhas[trilhaId];
      gravarTudo(agora);
    };

    // ---- caixas clicáveis --------------------------------------------------
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

    // ---- botões ------------------------------------------------------------
    const arquivo = painel.querySelector('.hum-input-arquivo');
    painel.querySelector('[data-acao="exportar"]').addEventListener('click', exportarJson);
    painel.querySelector('[data-acao="importar"]').addEventListener('click', () => arquivo.click());
    arquivo.addEventListener('change', () =>
      importarArquivo(arquivo, () => location.reload())
    );
    painel.querySelector('[data-acao="copiar-comando"]').addEventListener('click', async (e) => {
      const ok = await copiar(COMANDO);
      e.currentTarget.textContent = ok ? 'Copiado!' : 'Não consegui copiar';
      setTimeout(() => {
        e.currentTarget.textContent = 'Copiar comando';
      }, 1800);
    });
    painel.querySelector('[data-acao="limpar"]').addEventListener('click', () => {
      if (!confirm('Limpar a marcação local desta trilha? (o repositório não é afetado)')) return;
      const agora = lerTudo();
      delete agora.trilhas[trilhaId];
      gravarTudo(agora);
      itens.forEach((li) => {
        const input = li.querySelector('input');
        if (input) input.checked = false;
        li.classList.remove('hum-feito');
      });
      atualizarPainel();
    });
  }

  // ---- central de progresso (página Registrar) -----------------------------
  function iniciarCentral() {
    const caixa = document.querySelector('#hum-progresso');
    if (!caixa) return;

    let config = { trilhas: [] };
    try {
      config = JSON.parse(document.getElementById('hum-config').textContent);
    } catch {
      return;
    }
    const trilhas = config.trilhas || [];
    const linhas = caixa.querySelector('#hum-linhas-progresso');
    const totalTxt = caixa.querySelector('#hum-total-progresso');
    const arquivo = caixa.querySelector('.hum-input-arquivo');
    destinoAviso = caixa.querySelector('#hum-dica-progresso');

    const desenhar = () => {
      const tudo = lerTudo();
      let somaMarcados = 0;
      let somaTotal = 0;
      const usadas = [];

      linhas.innerHTML = '';
      trilhas.forEach((tr) => {
        const total = Number(tr.total) || 0;
        const marcados = marcadosDe(tudo, tr.slug).filter((i) => i < total);
        const feitos = marcados.length;
        somaMarcados += feitos;
        somaTotal += total;
        if (feitos) usadas.push(tr);

        const tr_ = document.createElement('tr');
        if (feitos) tr_.className = 'hum-linha-ativa';
        const pct = total ? Math.round((feitos * 100) / total) : 0;
        tr_.innerHTML = `
          <td><a href="trilhas/${tr.arquivo}">${tr.nome}</a></td>
          <td>
            <span class="hum-mini-barra"><span style="width:${pct}%"></span></span>
            <span class="hum-mini-contagem">${feitos}/${total}</span>
          </td>
          <td class="hum-mini-acao">${feitos ? 'rascunho local' : ''}</td>
        `;
        linhas.appendChild(tr_);
      });

      if (!linhas.children.length) {
        linhas.innerHTML = '<tr><td colspan="3">Nenhuma trilha encontrada no índice.</td></tr>';
      }

      if (!somaMarcados) {
        totalTxt.textContent =
          'Nada marcado neste navegador ainda. Abra uma trilha e clique nas caixas dos nós.';
      } else {
        totalTxt.textContent =
          `${somaMarcados} de ${somaTotal} nós marcados (${Math.round((somaMarcados * 100) / (somaTotal || 1))}%) ` +
          `em ${usadas.length} trilha(s).`;
      }
      return { tudo, usadas, somaMarcados };
    };

    desenhar();

    // resumo legível: bom para celular, impressão e backup "à prova de leitor"
    const baixarResumo = () => {
      const { tudo } = desenhar();
      const hoje = new Date().toISOString().slice(0, 10);
      const linhasMd = [
        `# Progresso — ${hoje}`,
        '',
        'Backup legível do progresso marcado no site. Para restaurar, use o',
        '`progresso.json` (este arquivo é só para leitura).',
        '',
      ];
      let algum = false;
      trilhas.forEach((tr) => {
        const marcados = new Set(marcadosDe(tudo, tr.slug));
        if (!marcados.size) return;
        algum = true;
        linhasMd.push(`## ${tr.nome}`, '');
        (tr.nos || []).forEach((no, i) => {
          linhasMd.push(`- [${marcados.has(i) ? 'x' : ' '}] ${no}`);
        });
        linhasMd.push('');
      });
      if (!algum) {
        alert('Nada marcado neste navegador: não há resumo para baixar.');
        return;
      }
      baixar(`progresso-${hoje}.md`, linhasMd.join('\n'), 'text/markdown');
      avisar('Resumo legível baixado — serve para consultar no celular ou imprimir.');
    };

    caixa.querySelector('[data-acao="exportar"]').addEventListener('click', exportarJson);
    caixa.querySelector('[data-acao="baixar-md"]').addEventListener('click', baixarResumo);
    caixa.querySelector('[data-acao="importar"]').addEventListener('click', () => arquivo.click());
    arquivo.addEventListener('change', () =>
      importarArquivo(arquivo, (quantas) => {
        desenhar();
        avisar(`Importado: ${quantas} trilha(s). O progresso do arquivo sobrescreveu o local nessas trilhas.`);
      })
    );
    caixa.querySelector('[data-acao="copiar-comando"]').addEventListener('click', async (e) => {
      const ok = await copiar(`cd ~/humanitas\n${COMANDO}`);
      e.currentTarget.textContent = ok ? 'Copiado!' : 'Não consegui copiar';
      setTimeout(() => {
        e.currentTarget.textContent = 'Copiar comando';
      }, 1800);
    });
    caixa.querySelector('[data-acao="limpar-tudo"]').addEventListener('click', () => {
      if (!confirm('Apagar o progresso marcado neste navegador (todas as trilhas)? O repositório não é afetado.')) return;
      gravarTudo({ trilhas: {} });
      desenhar();
      avisar('Progresso local apagado. Se tiver um backup, use "Importar…" para restaurar.');
    });
  }

  document.addEventListener('DOMContentLoaded', () => {
    if (document.querySelector('#hum-progresso')) iniciarCentral();
    else iniciarTrilha();
  });
})();
