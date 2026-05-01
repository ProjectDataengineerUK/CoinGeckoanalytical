const SAMPLE_RESPONSE = {
  request_id: "req_20260501_001",
  surface_type: "dashboard_payload",
  title: "Visao geral do mercado",
  body: "Painel governado com rankings, movers, dominancia e comparacoes para a rota dashboard.market-overview.",
  citations: [
    "gold_market_rankings",
    "gold_top_movers",
    "gold_market_dominance",
    "gold_cross_asset_comparison",
  ],
  freshness: { watermark: "2026-05-01T14:30:00Z", status: "ready" },
  confidence: { label: "governed", score: 0.9 },
  actions: ["open_asset_detail", "ask_genie_question", "open_copilot_context"],
  warnings: [],
  routing: {
    surface: "dashboard",
    route_id: "dashboard.market-overview",
    reason: "governed_market_overview_route",
  },
  payload: {
    route_id: "dashboard.market-overview",
    locale: "pt-BR",
    hero_metrics: {
      tracked_assets: 42,
      top_movers_visible: 3,
      dominance_groups_visible: 4,
    },
    sections: {
      market_rankings: [
        { asset: "BTC", name: "Bitcoin", market_cap_rank: 1, market_cap_usd: 1850000000000, price_usd: 95000 },
        { asset: "ETH", name: "Ethereum", market_cap_rank: 2, market_cap_usd: 420000000000, price_usd: 3200 },
      ],
      top_movers: [
        { asset: "SOL", direction: "positive", price_change_pct_24h: 9.4, move_band_24h: "medium" },
      ],
      dominance: [
        { group: "btc", dominance_pct: 52.8, market_cap_usd: 1850000000000 },
        { group: "eth", dominance_pct: 12.4, market_cap_usd: 420000000000 },
      ],
      comparisons: [
        { asset: "BTC", correlation_bucket: "large_cap", price_change_pct_24h: 3.1, price_change_pct_7d: 7.9 },
      ],
    },
  },
  schema_version: "coingecko.response.v1",
};

const SAMPLE_COPILOT_RESPONSE = {
  request_id: "req_20260501_002",
  surface_type: "copilot_answer",
  title: "Copilot de mercado",
  body: "Resposta de copilot MVP: use o agente para analise narrativa, com provenance, frescor e policy context.",
  citations: ["unity_catalog.gold_market_views", "mosaic_ai_vector_search"],
  freshness: { watermark: "pending", status: "unknown" },
  confidence: { label: "provisional", score: 0.64 },
  actions: ["follow_up_question", "open_analytics_view"],
  warnings: ["mvp_stub_response"],
  routing: {
    surface: "copilot",
    reason: "default_copilot_path",
    signals: [],
  },
  schema_version: "copilot.response.v1",
};

const state = {
  view: "dashboard",
  apiBaseUrl: window.__CGA_API_BASE__ || "",
};

const el = (id) => document.getElementById(id);

const dom = {
  responseRoute: el("response-route"),
  responseTitle: el("response-title"),
  responseBody: el("response-body"),
  responseFreshness: el("response-freshness"),
  responseConfidence: el("response-confidence"),
  responseCitations: el("response-citations"),
  responseJson: el("response-json"),
  dashboardSummary: el("dashboard-summary"),
  chatSummary: el("chat-summary"),
  navTabs: Array.from(document.querySelectorAll(".nav-tab")),
  messageText: el("message-text"),
  requestTypeHint: el("request-type-hint"),
  channel: el("channel"),
  selectedAssets: el("selected-assets"),
  timeRange: el("time-range"),
};

function formatCurrency(value) {
  return new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function renderSummaryLists() {
  const dashboardItems = [
    "Dashboard público externo",
    "Resposta guiada por BFF",
    "Sem credenciais Databricks no browser",
  ];
  const chatItems = [
    "Perguntas estruturadas seguem para Genie",
    "Perguntas narrativas seguem para copilot",
    "Envelope inclui frescura e confiança",
  ];

  dom.dashboardSummary.innerHTML = dashboardItems.map((item) => `<li>${item}</li>`).join("");
  dom.chatSummary.innerHTML = chatItems.map((item) => `<li>${item}</li>`).join("");
}

function renderResponse(response) {
  const route = response?.routing?.route_id || response?.routing?.surface || "unknown";
  dom.responseRoute.textContent = route;
  dom.responseTitle.textContent = response?.title || "Sem titulo";
  dom.responseBody.textContent = response?.body || "Sem corpo";
  dom.responseFreshness.textContent = response?.freshness?.watermark || response?.freshness?.status || "-";
  dom.responseConfidence.textContent = response?.confidence?.label
    ? `${response.confidence.label} (${Math.round((response.confidence.score || 0) * 100)}%)`
    : "-";
  dom.responseCitations.textContent = String(response?.citations?.length || 0);
  dom.responseJson.textContent = JSON.stringify(response, null, 2);
}

function collectRequestPayload() {
  return {
    tenant_id: el("tenant-id").value.trim(),
    user_id: el("user-id").value.trim(),
    session_id: el("session-id").value.trim(),
    request_id: `req_${Date.now()}`,
    locale: "pt-BR",
    plan_tier: el("plan-tier").value.trim(),
    channel: dom.channel.value,
    request_type_hint: dom.requestTypeHint.value,
    message_text: dom.messageText.value.trim(),
    selected_assets: dom.selectedAssets.value
      .split(",")
      .map((asset) => asset.trim())
      .filter(Boolean),
    time_range: { window: dom.timeRange.value.trim() },
  };
}

function inferLocalResponse(payload) {
  if (payload.request_type_hint === "dashboard_query" || payload.message_text.toLowerCase().includes("market overview")) {
    return SAMPLE_RESPONSE;
  }
  return SAMPLE_COPILOT_RESPONSE;
}

async function sendRequest() {
  const payload = collectRequestPayload();
  const baseUrl = state.apiBaseUrl.replace(/\/$/, "");

  if (!baseUrl) {
    renderResponse(inferLocalResponse(payload));
    return;
  }

  const response = await fetch(`${baseUrl}/routing`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(`BFF request failed: ${response.status}`);
  }

  renderResponse(await response.json());
}

function activateView(view) {
  state.view = view;
  dom.navTabs.forEach((tab) => {
    tab.classList.toggle("active", tab.dataset.view === view);
  });

  if (view === "dashboard") {
    dom.requestTypeHint.value = "dashboard_query";
    dom.messageText.value = "market overview";
  } else if (view === "chat") {
    dom.requestTypeHint.value = "copilot";
    dom.messageText.value = "What is driving BTC dominance today?";
  } else {
    dom.requestTypeHint.value = "auto";
    dom.messageText.value = "admin";
  }
}

function wireEvents() {
  dom.navTabs.forEach((tab) => {
    tab.addEventListener("click", () => activateView(tab.dataset.view));
  });

  el("load-sample").addEventListener("click", () => {
    renderResponse(inferLocalResponse(collectRequestPayload()));
  });

  el("send-request").addEventListener("click", () => {
    sendRequest().catch((error) => {
      renderResponse({
        request_id: "error",
        title: "Erro de BFF",
        body: error.message,
        surface_type: "error",
        citations: [],
        freshness: { watermark: null, status: "error" },
        confidence: { label: "low", score: 0 },
        actions: [],
        warnings: ["frontend_fetch_failed"],
        routing: { surface: "frontend", reason: "fetch_error", signals: [] },
        schema_version: "coingecko.response.v1",
      });
    });
  });
}

function bootstrap() {
  renderSummaryLists();
  renderResponse(inferLocalResponse(collectRequestPayload()));
  wireEvents();
}

bootstrap();
