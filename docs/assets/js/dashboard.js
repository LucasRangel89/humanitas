// Humanitas — Livro Digital Interativo: Leitor, Players, Filtros, Flashcards e Grafo
document.addEventListener('DOMContentLoaded', () => {
  const TEMA_CORES = {
    filosofia: '#2d6a64',
    sociologia: '#3b4cca',
    psicologia: '#b85d19',
    antropologia: '#8c3b5a',
    historia: '#7c5832',
    geografia: '#2f6f4e',
    'ciencia-politica': '#5b3e82',
    economia: '#1f5f7a',
    integrada: '#7a3e2e',
  };

  // =========================================================================
  // 1. Barra de Progresso de Leitura & Controles de Leitor (A-, A+, Modo Foco)
  // =========================================================================
  const progressBar = document.createElement('div');
  progressBar.id = 'eb-reading-progress';
  document.body.appendChild(progressBar);

  const updateReadingProgress = () => {
    const doc = document.documentElement;
    const scrollTop = doc.scrollTop || document.body.scrollTop;
    const scrollHeight = doc.scrollHeight - doc.clientHeight;
    const pct = scrollHeight > 40 ? Math.min(100, Math.max(0, (scrollTop / scrollHeight) * 100)) : 0;
    progressBar.style.width = `${pct}%`;
  };
  window.addEventListener('scroll', updateReadingProgress, { passive: true });
  updateReadingProgress();

  // Controles de tipografia e Modo Foco (salvos no localStorage)
  const PREFS_KEY = 'humanitas.leitor.v1';
  let prefs = { scale: 1, zen: false };
  try {
    prefs = { ...prefs, ...JSON.parse(localStorage.getItem(PREFS_KEY) || '{}') };
  } catch { /* ignore */ }

  const applyReaderPrefs = () => {
    document.body.style.setProperty('--eb-font-scale', String(prefs.scale || 1));
    document.body.classList.toggle('eb-zen-mode', Boolean(prefs.zen));
    const zenBtn = document.querySelector('[data-reader="zen"]');
    if (zenBtn) {
      zenBtn.classList.toggle('active', Boolean(prefs.zen));
      zenBtn.setAttribute('aria-pressed', String(Boolean(prefs.zen)));
    }
  };

  const controls = document.createElement('div');
  controls.className = 'eb-reader-controls';
  controls.setAttribute('aria-label', 'Preferências de leitura');
  controls.innerHTML = `
    <button type="button" data-reader="font-down" title="Diminuir fonte">A−</button>
    <button type="button" data-reader="font-up" title="Aumentar fonte">A+</button>
    <button type="button" data-reader="zen" title="Alternar modo foco de leitura" aria-pressed="false">📖 Foco</button>
  `;
  document.body.appendChild(controls);
  applyReaderPrefs();

  controls.addEventListener('click', (e) => {
    const btn = e.target.closest('button[data-reader]');
    if (!btn) return;
    const action = btn.dataset.reader;
    if (action === 'font-down') prefs.scale = Math.max(0.88, Math.round((prefs.scale - 0.06) * 100) / 100);
    if (action === 'font-up') prefs.scale = Math.min(1.24, Math.round((prefs.scale + 0.06) * 100) / 100);
    if (action === 'zen') prefs.zen = !prefs.zen;
    applyReaderPrefs();
    try { localStorage.setItem(PREFS_KEY, JSON.stringify(prefs)); } catch { /* ignore */ }
  });

  // =========================================================================
  // 2. Marcador de Página Automático & Sincronia Visual dos Volumes com localStorage
  // =========================================================================
  const BOOKMARK_KEY = 'humanitas.marcador.v1';
  const path = window.location.pathname;
  if (path.includes('/trilhas/') || path.includes('/conceitos/')) {
    const h1 = document.querySelector('.md-content h1');
    if (h1 && !path.endsWith('/trilhas/') && !path.endsWith('/conceitos/')) {
      try {
        localStorage.setItem(
          BOOKMARK_KEY,
          JSON.stringify({
            url: window.location.href,
            titulo: h1.textContent.trim(),
            tipo: path.includes('/trilhas/') ? 'Volume' : 'Ensaio',
            em: new Date().toISOString(),
          })
        );
      } catch { /* ignore */ }
    }
  }

  // Atualiza cartões de volume na Capa e no Sumário com o progresso salvo localmente
  try {
    const progLocal = JSON.parse(localStorage.getItem('humanitas.progresso.v1') || '{}');
    const trilhasLocais = progLocal.trilhas || {};
    document.querySelectorAll('.eb-volume-card[data-trilha-slug]').forEach((card) => {
      const slug = card.dataset.trilhaSlug;
      const total = Number(card.dataset.trilhaTotal) || 0;
      const feitos = Array.isArray(trilhasLocais[slug]) ? trilhasLocais[slug].filter((i) => i < total).length : 0;
      if (feitos > 0 && total > 0) {
        const stopsEl = card.querySelector('.eb-vol-stops');
        const pct = Math.round((feitos * 100) / total);
        if (stopsEl) stopsEl.textContent = `✔ ${feitos}/${total} paradas · ${pct}% (seu progresso)`;
      }
    });

    const marcador = JSON.parse(localStorage.getItem(BOOKMARK_KEY) || 'null');
    const primaryCta = document.getElementById('eb-primary-cta');
    if (marcador && marcador.url && marcador.titulo && primaryCta) {
      const resumeLink = document.createElement('a');
      resumeLink.className = 'eb-btn-secondary';
      resumeLink.href = marcador.url;
      resumeLink.textContent = `🔖 Continuar onde parou: ${marcador.titulo.slice(0, 38)}`;
      primaryCta.insertAdjacentElement('afterend', resumeLink);
    }
  } catch { /* ignore */ }

  // =========================================================================
  // 3. Player Audiovisual In-Page (YouTube Privacy-Enhanced sob demanda)
  // =========================================================================
  document.addEventListener('click', (e) => {
    const playBtn = e.target.closest('.eb-media-play[data-embed]');
    if (!playBtn) return;
    const card = playBtn.closest('.eb-media-card');
    const slot = card?.querySelector('.eb-media-player');
    if (!slot) return;

    const isOpen = !slot.hidden;
    if (isOpen) {
      slot.innerHTML = '';
      slot.hidden = true;
      playBtn.setAttribute('aria-expanded', 'false');
      playBtn.textContent = '▶ Assistir na página';
    } else {
      const src = playBtn.dataset.embed;
      slot.innerHTML = `<iframe src="${src}" title="Reprodutor de aula" loading="lazy" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" allowfullscreen></iframe>`;
      slot.hidden = false;
      playBtn.setAttribute('aria-expanded', 'true');
      playBtn.textContent = '✕ Fechar vídeo';
    }
  });

  // =========================================================================
  // 4. Atlas de Conceitos: Busca + Filtro por Tema + Filtro Conceito/Eixo + Hash
  // =========================================================================
  const searchInput = document.getElementById('humanitas-search');
  const filterButtons = document.querySelectorAll('.humanitas-filter[data-filter]');
  const tipoButtons = document.querySelectorAll('[data-tipo-filter]');
  const cards = document.querySelectorAll('.conceito-card');
  let activeFilter = 'todos';
  let activeTipo = 'todos';

  function applyConceitoFilters() {
    if (!cards.length) return;
    const q = (searchInput?.value || '').toLowerCase().trim();
    let visible = 0;
    cards.forEach((card) => {
      const tema = card.dataset.tema || '';
      const tipo = card.dataset.tipo || 'conceito';
      const texto = card.innerText.toLowerCase();
      const matchTema = activeFilter === 'todos' || tema === activeFilter;
      const matchTipo = activeTipo === 'todos' || tipo === activeTipo;
      const matchQ = !q || texto.includes(q);
      const show = matchTema && matchTipo && matchQ;
      card.style.display = show ? '' : 'none';
      if (show) visible += 1;
    });
    const counter = document.getElementById('conceito-counter');
    if (counter) counter.textContent = `Exibindo ${visible} de ${cards.length} verbetes`;
  }

  if (cards.length) {
    // Se a URL tiver #sociologia, ativa o filtro do tema automaticamente
    const hashTema = window.location.hash.replace('#', '').trim();
    if (hashTema) {
      const matchingBtn = [...filterButtons].find((b) => b.dataset.filter === hashTema);
      if (matchingBtn) {
        filterButtons.forEach((b) => b.classList.remove('active'));
        matchingBtn.classList.add('active');
        activeFilter = hashTema;
      }
    }
    searchInput?.addEventListener('input', applyConceitoFilters);
    filterButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        filterButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        activeFilter = btn.dataset.filter || 'todos';
        applyConceitoFilters();
      });
    });
    tipoButtons.forEach((btn) => {
      btn.addEventListener('click', () => {
        tipoButtons.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        activeTipo = btn.dataset.tipoFilter || 'todos';
        applyConceitoFilters();
      });
    });
    applyConceitoFilters();
  }

  // =========================================================================
  // 5. Cinemateca (`midias.md`): Busca + Filtro por Tema + Filtro por Camada/Peso
  // =========================================================================
  const mediaSearch = document.getElementById('eb-media-search');
  const mediaSections = document.querySelectorAll('.eb-media-theme-section');
  if (mediaSections.length) {
    let mTema = 'todos';
    let mPeso = 'todos';
    const temaBtns = document.querySelectorAll('[data-media-tema]');
    const pesoBtns = document.querySelectorAll('[data-media-peso]');
    const counterEl = document.getElementById('eb-media-counter');
    const allMediaCards = document.querySelectorAll('.eb-media-theme-section .eb-media-card');

    const applyMediaFilters = () => {
      const q = (mediaSearch?.value || '').toLowerCase().trim();
      let totalVisiveis = 0;

      mediaSections.forEach((sec) => {
        const secTema = sec.dataset.themeSection || '';
        const temaOk = mTema === 'todos' || secTema === mTema;
        let visiveisSec = 0;

        sec.querySelectorAll('.eb-media-card').forEach((card) => {
          const cardPeso = card.dataset.peso || '';
          const pesoOk = mPeso === 'todos' || cardPeso === mPeso;
          const qOk = !q || card.innerText.toLowerCase().includes(q);
          const show = temaOk && pesoOk && qOk;
          card.style.display = show ? '' : 'none';
          if (show) visiveisSec += 1;
        });

        sec.style.display = visiveisSec > 0 ? '' : 'none';
        totalVisiveis += visiveisSec;
      });

      if (counterEl) {
        counterEl.textContent = `Exibindo ${totalVisiveis} de ${allMediaCards.length} indicações verificadas`;
      }
    };

    mediaSearch?.addEventListener('input', applyMediaFilters);
    temaBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        temaBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        mTema = btn.dataset.mediaTema || 'todos';
        applyMediaFilters();
      });
    });
    pesoBtns.forEach((btn) => {
      btn.addEventListener('click', () => {
        pesoBtns.forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        mPeso = btn.dataset.mediaPeso || 'todos';
        applyMediaFilters();
      });
    });
    applyMediaFilters();
  }

  // Atalho de teclado `/` ou `Ctrl+K` para focar busca da página atual
  document.addEventListener('keydown', (e) => {
    const targetInput = searchInput || mediaSearch;
    if (!targetInput) return;
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      targetInput.focus();
    } else if (e.key === '/' && !['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement?.tagName || '')) {
      e.preventDefault();
      targetInput.focus();
    }
  });

  // =========================================================================
  // 6. Treinador Interativo de Flashcards (`retencao.md`)
  // =========================================================================
  const fcDataEl = document.getElementById('eb-flashcards-data');
  const fcTrainer = document.getElementById('eb-flashcard-trainer');
  if (fcDataEl && fcTrainer) {
    let deck = [];
    try { deck = JSON.parse(fcDataEl.textContent || '[]'); } catch { deck = []; }
    if (deck.length) {
      let idx = 0;
      let flipped = false;
      const elTheme = document.getElementById('eb-fc-theme');
      const elFront = document.getElementById('eb-fc-front');
      const elBack = document.getElementById('eb-fc-back');
      const elProg = document.getElementById('eb-fc-progress');
      const elFlipBtn = document.getElementById('eb-fc-flip');
      const elOpen = document.getElementById('eb-fc-open');
      const elStage = document.getElementById('eb-fc-stage');

      const renderCard = () => {
        const item = deck[idx];
        elTheme.textContent = `${item.tema} · ${item.tipo === 'eixo' ? 'Eixo de debate' : 'Conceito'}`;
        elFront.textContent = item.tipo === 'eixo'
          ? `Qual é a questão central do eixo «${item.conceito}»?`
          : `O que é «${item.conceito}»?`;
        elBack.textContent = item.definicao;
        elBack.hidden = !flipped;
        elFlipBtn.textContent = flipped ? 'Ocultar resposta' : 'Revelar resposta';
        elProg.textContent = `Cartão ${idx + 1} de ${deck.length}`;
        if (elOpen) {
          const slug = item.arquivo.replace(/\.md$/, '');
          elOpen.href = `../conceitos/${slug}/`;
        }
      };

      const toggleFlip = () => {
        flipped = !flipped;
        renderCard();
      };

      elStage?.addEventListener('click', toggleFlip);
      elStage?.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Enter') {
          e.preventDefault();
          toggleFlip();
        }
      });
      elFlipBtn?.addEventListener('click', toggleFlip);
      document.getElementById('eb-fc-prev')?.addEventListener('click', () => {
        idx = (idx - 1 + deck.length) % deck.length;
        flipped = false;
        renderCard();
      });
      document.getElementById('eb-fc-next')?.addEventListener('click', () => {
        idx = (idx + 1) % deck.length;
        flipped = false;
        renderCard();
      });
      document.getElementById('eb-fc-shuffle')?.addEventListener('click', () => {
        deck = [...deck].sort(() => Math.random() - 0.5);
        idx = 0;
        flipped = false;
        renderCard();
      });
      renderCard();
    }
  }

  // =========================================================================
  // 7. Grafo Interativo Completo (96 nós, cores por disciplina, filtro e links corretos)
  // =========================================================================
  const grafoCanvas = document.getElementById('grafo-canvas');
  if (grafoCanvas) {
    const urls = ['indices/grafo.json', '../indices/grafo.json', '../../indices/grafo.json'];
    const tryFetch = (i) => {
      if (i >= urls.length) return;
      fetch(urls[i])
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((data) => renderGrafo(grafoCanvas, data, urls[i].replace('indices/grafo.json', '')))
        .catch(() => tryFetch(i + 1));
    };
    tryFetch(0);
  }

  function renderGrafo(canvas, data, basePrefix) {
    if (!data || !Array.isArray(data.nodes) || !data.nodes.length) return;

    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    const rectInit = canvas.parentElement.getBoundingClientRect();
    const width = Math.max(320, Math.floor(rectInit.width || 800));
    const height = Math.max(320, Math.floor(rectInit.height || 420));
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    const ctx = canvas.getContext('2d');
    ctx.scale(dpr, dpr);

    let graphFilter = 'todos';
    const allNodes = data.nodes.map((n, i) => {
      const angle = (i / data.nodes.length) * Math.PI * 2;
      const radius = n.tipo === 'eixo' ? Math.min(width, height) * 0.18 : Math.min(width, height) * 0.36;
      return {
        ...n,
        x: width / 2 + Math.cos(angle) * radius + (Math.random() - 0.5) * 30,
        y: height / 2 + Math.sin(angle) * radius + (Math.random() - 0.5) * 30,
        vx: 0,
        vy: 0,
        r: n.tipo === 'eixo' ? 8.5 : 5.8,
        color: n.tipo === 'eixo' ? '#c0392b' : (TEMA_CORES[n.tema] || '#5c4938'),
      };
    });

    const map = Object.fromEntries(allNodes.map((n) => [n.id, n]));
    const allEdges = (data.edges || []).filter((e) => map[e.source] && map[e.target]);

    let hover = null;
    let dragging = null;
    let cooling = 1.0;

    const isNodeVisible = (n) => graphFilter === 'todos' || n.tema === graphFilter || n.tipo === 'eixo';

    document.querySelectorAll('[data-graph-tema]').forEach((btn) => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('[data-graph-tema]').forEach((b) => b.classList.remove('active'));
        btn.classList.add('active');
        graphFilter = btn.dataset.graphTema || 'todos';
        cooling = 0.6;
        requestAnimationFrame(step);
      });
    });

    function step() {
      const nodes = allNodes.filter(isNodeVisible);
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i];
          const b = nodes[j];
          const dx = a.x - b.x;
          const dy = a.y - b.y;
          const d2 = dx * dx + dy * dy || 1;
          if (d2 < 8500) {
            const d = Math.sqrt(d2);
            const f = ((92 - d) * 0.018) * cooling;
            a.vx += (dx / d) * f;
            a.vy += (dy / d) * f;
            b.vx -= (dx / d) * f;
            b.vy -= (dy / d) * f;
          }
        }
      }

      allEdges.forEach((e) => {
        const a = map[e.source];
        const b = map[e.target];
        if (!a || !b || !isNodeVisible(a) || !isNodeVisible(b)) return;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const d = Math.sqrt(dx * dx + dy * dy) || 1;
        const ideal = e.tipo === 'eixo' ? 115 : 85;
        const f = (d - ideal) * 0.008 * cooling;
        a.vx += (dx / d) * f;
        a.vy += (dy / d) * f;
        b.vx -= (dx / d) * f;
        b.vy -= (dy / d) * f;
      });

      // Gravidade suave para o centro
      nodes.forEach((n) => {
        if (n === dragging) return;
        n.vx += (width / 2 - n.x) * 0.0015 * cooling;
        n.vy += (height / 2 - n.y) * 0.0015 * cooling;
        n.x += n.vx;
        n.y += n.vy;
        n.vx *= 0.82;
        n.vy *= 0.82;
        n.x = Math.max(24, Math.min(width - 24, n.x));
        n.y = Math.max(24, Math.min(height - 24, n.y));
      });

      draw();
      cooling *= 0.992;
      if (cooling > 0.03 || dragging) {
        requestAnimationFrame(step);
      }
    }

    function draw() {
      const isDark = document.body.getAttribute('data-md-color-scheme') === 'slate';
      ctx.clearRect(0, 0, width, height);

      // Arestas
      allEdges.forEach((e) => {
        const a = map[e.source];
        const b = map[e.target];
        if (!a || !b || !isNodeVisible(a) || !isNodeVisible(b)) return;
        const highlighted = hover && (hover.id === a.id || hover.id === b.id);
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.lineWidth = highlighted ? 1.8 : 0.9;
        ctx.strokeStyle = highlighted
          ? (isDark ? 'rgba(226,149,120,0.85)' : 'rgba(122,59,46,0.75)')
          : (isDark ? 'rgba(235,229,220,0.13)' : 'rgba(46,36,24,0.13)');
        ctx.stroke();
      });

      // Nós
      allNodes.forEach((n) => {
        if (!isNodeVisible(n)) return;
        const isHover = hover === n;
        const isNeighbor = hover && allEdges.some(
          (e) => (e.source === hover.id && e.target === n.id) || (e.target === hover.id && e.source === n.id)
        );
        ctx.beginPath();
        ctx.arc(n.x, n.y, isHover ? n.r + 2.8 : n.r, 0, Math.PI * 2);
        ctx.fillStyle = n.color;
        ctx.globalAlpha = hover && !isHover && !isNeighbor ? 0.32 : 1;
        ctx.fill();
        ctx.lineWidth = isHover ? 2.2 : 1.2;
        ctx.strokeStyle = isDark ? '#171513' : '#faf7f2';
        ctx.stroke();
        ctx.globalAlpha = 1;

        // Rótulo fixo para eixos ou quando em destaque
        if (n.tipo === 'eixo' || isHover || isNeighbor) {
          ctx.font = `${isHover || n.tipo === 'eixo' ? '600 11.5px' : '500 10.5px'} Georgia, serif`;
          const txt = n.conceito;
          const tw = ctx.measureText(txt).width;
          const lx = Math.min(width - tw - 10, Math.max(6, n.x + 10));
          const ly = Math.max(16, n.y - 8);
          ctx.fillStyle = isDark ? 'rgba(23,21,19,0.86)' : 'rgba(250,247,242,0.88)';
          ctx.fillRect(lx - 3, ly - 11, tw + 6, 15);
          ctx.fillStyle = isDark ? '#ebe5dc' : '#1e1b18';
          ctx.fillText(txt, lx, ly);
        }
      });
    }

    const getCoords = (e) => {
      const rect = canvas.getBoundingClientRect();
      return {
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      };
    };

    canvas.addEventListener('mousemove', (e) => {
      const { x, y } = getCoords(e);
      if (dragging) {
        dragging.x = x;
        dragging.y = y;
        draw();
        return;
      }
      const prev = hover;
      hover = allNodes.find((n) => isNodeVisible(n) && Math.hypot(n.x - x, n.y - y) < n.r + 6) || null;
      canvas.style.cursor = hover ? 'pointer' : 'grab';
      if (hover !== prev) draw();
    });

    let movedWhileDown = false;
    canvas.addEventListener('mousedown', (e) => {
      const { x, y } = getCoords(e);
      const hit = allNodes.find((n) => isNodeVisible(n) && Math.hypot(n.x - x, n.y - y) < n.r + 6);
      movedWhileDown = false;
      if (hit) {
        dragging = hit;
        cooling = Math.max(cooling, 0.25);
        requestAnimationFrame(step);
      }
    });
    window.addEventListener('mousemove', () => {
      if (dragging) movedWhileDown = true;
    });
    window.addEventListener('mouseup', () => {
      dragging = null;
    });

    canvas.addEventListener('click', () => {
      if (hover && !movedWhileDown) {
        const slug = hover.id.replace(/\.md$/, '');
        window.location.href = `${basePrefix}conceitos/${slug}/`;
      }
    });

    requestAnimationFrame(step);
  }
});
