/* ============================================================================
   Observatório Rural Paranaense — render dos eixos / camadas / núcleo
   Vanilla JS, sem dependências externas. Lê assets/data/eixos.json.
   Toda a marca/cores vêm de tokens.css; nenhum painel é hardcoded aqui.
   ========================================================================= */
(function () {
  'use strict';

  var DATA_URL = 'assets/data/eixos.json';

  /* Rótulos legíveis por status (chips). Fallback para o próprio valor. */
  var STATUS_ROTULO = {
    ativo: 'Ativo',
    planejado: 'Planejado',
    contextual: 'Contextual',
    interno: 'Interno'
  };

  /* ---- Helpers DOM seguros (escape de texto evita XSS) ------------------- */

  // Cria elemento com texto via textContent (nunca innerHTML com dado externo).
  function el(tag, className, text) {
    var node = document.createElement(tag);
    if (className) { node.className = className; }
    if (text != null) { node.textContent = String(text); }
    return node;
  }

  function statusRotulo(status) {
    if (typeof status !== 'string') { return 'Status'; }
    return STATUS_ROTULO[status] || status;
  }

  // Chip de status com classe segura (classe só do mapa conhecido).
  function chip(status) {
    var safe = (typeof status === 'string' && STATUS_ROTULO[status]) ? status : 'planejado';
    var node = el('span', 'chip chip--' + safe, statusRotulo(status));
    return node;
  }

  function mostrarErro(container, mensagem) {
    if (!container) { return; }
    container.setAttribute('aria-busy', 'false');
    container.replaceChildren();
    var p = el('p', 'estado-erro', mensagem);
    container.appendChild(p);
  }

  /* ---- Render de um painel (link em nova aba ou item planejado) ---------- */
  function renderPainel(painel) {
    var temUrl = painel && typeof painel.url === 'string' && painel.url.length > 0;
    var status = painel && painel.status ? painel.status : 'planejado';
    var nome = painel && painel.nome ? painel.nome : 'Painel';

    var node;
    if (temUrl) {
      node = el('a', 'painel');
      node.href = painel.url;
      node.target = '_blank';
      node.rel = 'noopener noreferrer';
      node.setAttribute('aria-label', nome + ' — abre em nova aba (status: ' + statusRotulo(status) + ')');
    } else {
      // Painéis sem URL: item não-clicável marcado como planejado.
      node = el('span', 'painel painel--planejado');
    }

    node.appendChild(el('span', 'painel__nome', nome));
    node.appendChild(temUrl ? chip(status) : chip('planejado'));
    return node;
  }

  /* ---- Render de um card de eixo ----------------------------------------- */
  function renderEixo(eixo) {
    var card = el('article', 'eixo-card');

    var top = el('div', 'eixo-card__top');
    var num = el('span', 'eixo-card__num', String(eixo.ordem != null ? eixo.ordem : ''));
    num.setAttribute('aria-hidden', 'true');

    var head = el('div', 'eixo-card__head');
    var h3 = el('h3', 'eixo-card__nome', eixo.nome || 'Eixo');
    head.appendChild(h3);

    if (eixo.piloto === true) {
      var badges = el('div', 'eixo-card__badges');
      badges.appendChild(el('span', 'badge badge--piloto', 'piloto'));
      head.appendChild(badges);
    }

    top.appendChild(num);
    top.appendChild(head);
    card.appendChild(top);

    if (eixo.descricao) {
      card.appendChild(el('p', 'eixo-card__desc', eixo.descricao));
    }

    var paineis = Array.isArray(eixo.paineis) ? eixo.paineis : [];
    if (paineis.length > 0) {
      var lista = el('div', 'paineis');
      lista.setAttribute('role', 'list');
      paineis.forEach(function (p) {
        var item = renderPainel(p);
        item.setAttribute('role', 'listitem');
        lista.appendChild(item);
      });
      card.appendChild(lista);
    }

    return card;
  }

  /* ---- Render: seção de eixos -------------------------------------------- */
  function renderEixos(container, eixos) {
    if (!container) { return; }
    container.setAttribute('aria-busy', 'false');
    container.replaceChildren();

    if (!Array.isArray(eixos) || eixos.length === 0) {
      mostrarErro(container, 'Nenhum eixo temático disponível no momento.');
      return;
    }

    // Ordena por .ordem (cópia — não muta o array original).
    var ordenados = eixos.slice().sort(function (a, b) {
      var oa = (a && typeof a.ordem === 'number') ? a.ordem : Number.MAX_SAFE_INTEGER;
      var ob = (b && typeof b.ordem === 'number') ? b.ordem : Number.MAX_SAFE_INTEGER;
      return oa - ob;
    });

    var frag = document.createDocumentFragment();
    ordenados.forEach(function (eixo) {
      if (eixo) { frag.appendChild(renderEixo(eixo)); }
    });
    container.appendChild(frag);
  }

  /* ---- Render: camadas contextuais --------------------------------------- */
  function renderContextuais(container, camadas) {
    if (!container) { return; }
    container.setAttribute('aria-busy', 'false');
    container.replaceChildren();

    if (!Array.isArray(camadas) || camadas.length === 0) {
      mostrarErro(container, 'Nenhuma camada contextual disponível no momento.');
      return;
    }

    var frag = document.createDocumentFragment();
    camadas.forEach(function (camada) {
      if (!camada) { return; }
      var temUrl = typeof camada.url === 'string' && camada.url.length > 0;
      var status = camada.status || 'contextual';
      var nome = camada.nome || 'Camada';

      var card;
      if (temUrl) {
        card = el('a', 'contextual-card');
        card.href = camada.url;
        card.target = '_blank';
        card.rel = 'noopener noreferrer';
        card.setAttribute('aria-label', nome + ' — abre em nova aba');
      } else {
        card = el('div', 'contextual-card');
      }

      var info = el('div', 'contextual-card__info');
      info.appendChild(el('span', 'contextual-card__nome', nome));
      if (Array.isArray(camada.fontes) && camada.fontes.length > 0) {
        info.appendChild(el('span', 'contextual-card__fontes', 'Fontes: ' + camada.fontes.join(', ')));
      }
      card.appendChild(info);
      card.appendChild(chip(status));
      frag.appendChild(card);
    });
    container.appendChild(frag);
  }

  /* ---- Render: núcleo de inteligência ------------------------------------ */
  function renderNucleo(container, nucleo) {
    if (!container) { return; }
    container.setAttribute('aria-busy', 'false');
    container.replaceChildren();

    if (!nucleo || typeof nucleo !== 'object') {
      mostrarErro(container, 'Informações do núcleo de inteligência indisponíveis.');
      return;
    }

    var top = el('div', 'nucleo__top');
    top.appendChild(el('h3', 'nucleo__nome', nucleo.nome || 'Núcleo de inteligência territorial'));
    top.appendChild(chip(nucleo.status || 'planejado'));
    container.appendChild(top);

    if (nucleo.obs) {
      container.appendChild(el('p', 'nucleo__obs', nucleo.obs));
    }
    if (nucleo.repo) {
      var repo = el('p', 'nucleo__repo');
      repo.appendChild(el('span', null, 'Repositório de origem: '));
      repo.appendChild(el('code', null, nucleo.repo));
      container.appendChild(repo);
    }
  }

  /* ---- Boot: fetch + render com tratamento de erro amigável -------------- */
  function init() {
    var elEixos = document.getElementById('eixos');
    var elContextuais = document.getElementById('contextuais');
    var elNucleo = document.getElementById('nucleo');

    fetch(DATA_URL, { cache: 'no-cache' })
      .then(function (resp) {
        if (!resp.ok) {
          throw new Error('Resposta HTTP ' + resp.status);
        }
        return resp.json();
      })
      .then(function (dados) {
        if (!dados || typeof dados !== 'object') {
          throw new Error('Formato de dados inesperado.');
        }
        renderEixos(elEixos, dados.eixos);
        renderContextuais(elContextuais, dados.camadas_contextuais);
        renderNucleo(elNucleo, dados.nucleo_inteligencia);
      })
      .catch(function (err) {
        var msg = 'Não foi possível carregar os dados dos eixos no momento. '
          + 'Tente recarregar a página em instantes.';
        mostrarErro(elEixos, msg);
        mostrarErro(elContextuais, msg);
        mostrarErro(elNucleo, msg);
        if (window.console && console.error) {
          console.error('[Observatório Rural Paranaense] Falha ao carregar eixos.json:', err);
        }
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
