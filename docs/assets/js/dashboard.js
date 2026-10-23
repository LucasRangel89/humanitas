// Humanitas Dashboard — filtros e grafo
document.addEventListener('DOMContentLoaded', () => {
  // Filtros de conceitos
  const searchInput = document.getElementById('humanitas-search');
  const filterButtons = document.querySelectorAll('.humanitas-filter');
  const cards = document.querySelectorAll('.conceito-card');
  let activeFilter = 'todos';

  function applyFilters() {
    const q = (searchInput?.value || '').toLowerCase().trim();
    cards.forEach(card => {
      const tema = card.dataset.tema || '';
      const texto = card.innerText.toLowerCase();
      const matchTema = activeFilter === 'todos' || tema === activeFilter;
      const matchQ = !q || texto.includes(q);
      card.style.display = (matchTema && matchQ) ? '' : 'none';
    });
    // atualizar contador
    const visible = [...cards].filter(c => c.style.display !== 'none').length;
    const counter = document.getElementById('conceito-counter');
    if (counter) counter.textContent = `${visible} de ${cards.length} conceitos visíveis`;
  }

  searchInput?.addEventListener('input', applyFilters);
  filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      filterButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeFilter = btn.dataset.filter;
      applyFilters();
    });
  });

  // Atalho Ctrl+K / Cmd+K foca busca
  document.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      searchInput?.focus();
    }
    if (e.key === '/' && document.activeElement.tagName !== 'INPUT') {
      e.preventDefault();
      searchInput?.focus();
    }
  });

  // Grafo simples (sem dependência externa) — força layout
  const grafoContainer = document.getElementById('grafo-canvas');
  if (grafoContainer) {
    fetch('../indices/grafo.json')
      .then(r => r.json())
      .then(data => renderGrafo(grafoContainer, data))
      .catch(() => fetch('indices/grafo.json').then(r => r.json()).then(data => renderGrafo(grafoContainer, data)).catch(()=>{}));
  }

  function renderGrafo(container, data) {
    if (!data || !data.nodes) return;
    const width = container.clientWidth || 600;
    const height = 400;
    container.width = width;
    container.height = height;
    const ctx = container.getContext('2d');
    const nodes = data.nodes.slice(0, 40).map((n, i) => ({
      ...n,
      x: Math.random() * width,
      y: Math.random() * height,
      vx: 0, vy: 0,
      color: n.tipo === 'eixo' ? '#e91e63' : (n.tema === 'sociologia' ? '#3f51b5' : n.tema === 'filosofia' ? '#009688' : '#ff9800')
    }));
    const edges = (data.edges || []).filter(e => nodes.find(n => n.id === e.source) && nodes.find(n => n.id === e.target)).slice(0, 60);

    // mapa id -> node
    const map = Object.fromEntries(nodes.map(n => [n.id, n]));
    let hover = null;

    function tick() {
      // forças simples
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const a = nodes[i], b = nodes[j];
          const dx = a.x - b.x, dy = a.y - b.y;
          const d = Math.sqrt(dx*dx + dy*dy) || 1;
          if (d < 80) {
            const f = (80 - d) * 0.02;
            a.vx += dx/d * f; a.vy += dy/d * f;
            b.vx -= dx/d * f; b.vy -= dy/d * f;
          }
        }
      }
      edges.forEach(e => {
        const a = map[e.source], b = map[e.target];
        if (!a || !b) return;
        const dx = b.x - a.x, dy = b.y - a.y;
        const d = Math.sqrt(dx*dx + dy*dy) || 1;
        const f = (d - 100) * 0.01;
        a.vx += dx/d * f; a.vy += dy/d * f;
        b.vx -= dx/d * f; b.vy -= dy/d * f;
      });
      nodes.forEach(n => {
        n.x += n.vx; n.y += n.vy;
        n.vx *= 0.85; n.vy *= 0.85;
        n.x = Math.max(20, Math.min(width-20, n.x));
        n.y = Math.max(20, Math.min(height-20, n.y));
      });
      draw();
    }

    function draw() {
      ctx.clearRect(0, 0, width, height);
      // edges
      ctx.strokeStyle = '#ddd';
      ctx.lineWidth = 1;
      edges.forEach(e => {
        const a = map[e.source], b = map[e.target];
        if (!a || !b) return;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      });
      // nodes
      nodes.forEach(n => {
        ctx.beginPath();
        ctx.arc(n.x, n.y, n === hover ? 8 : 6, 0, Math.PI*2);
        ctx.fillStyle = n.color;
        ctx.fill();
        if (hover === n) {
          ctx.fillStyle = 'rgba(0,0,0,0.8)';
          ctx.font = '12px sans-serif';
          ctx.fillText(n.conceito, n.x + 10, n.y - 10);
        }
      });
    }

    container.addEventListener('mousemove', (e) => {
      const rect = container.getBoundingClientRect();
      const x = (e.clientX - rect.left) * (container.width / rect.width);
      const y = (e.clientY - rect.top) * (container.height / rect.height);
      hover = nodes.find(n => Math.hypot(n.x - x, n.y - y) < 12) || null;
      container.style.cursor = hover ? 'pointer' : 'default';
    });
    container.addEventListener('click', () => {
      if (hover) {
        // navega para conceito
        const alvo = hover.id.replace('.md', '');
        window.location.href = `conceitos/${alvo}.html` || `conceitos/${hover.id}`;
      }
    });

    setInterval(tick, 30);
    draw();
  }
});
