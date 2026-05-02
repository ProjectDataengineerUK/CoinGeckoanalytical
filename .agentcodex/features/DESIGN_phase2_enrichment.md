# DESIGN — Phase 2 Enrichment Pipeline

> **Status:** Designed
> **Phase:** 2 (post-ingestion enrichment)
> **Author:** Design Agent
> **Date:** 2026-05-02
> **Project:** CoinGeckoAnalytical
> **Builds on:** `.agentcodex/features/DESIGN_coingeckoanalytical.md`, Phase 1 Bronze→Silver→Gold→ai_serving live chain

---

## 1. Overview and Goals

### 1.1 Goal

Extend the existing CoinGecko-based Medallion pipeline with three free, publicly available enrichment sources that add fundamental, on-chain, and macro context to the market intelligence surface served to Genie and the external frontend:

1. **DefiLlama** — DeFi protocol fundamentals (TVL, fees, revenue) joined to the existing asset universe.
2. **GitHub** — Repository activity (stars, forks, commits, contributors) for assets that have public source code, used to compute a `dev_activity_score`.
3. **FRED** — Macro context series (DXY, DGS10, M2SL, CPIAUCSL) that situates crypto market state within the broader macroeconomic regime.

### 1.2 Non-goals

- No new ingestion sources beyond DefiLlama / GitHub / FRED in this phase.
- No alternative CoinGecko replacements; CoinGecko remains the canonical asset-of-record.
- No real-time / streaming layer; freshness budgets in this phase are 6 h (DeFi/GitHub) and 24 h (FRED).
- No AI/ML scoring beyond a deterministic, formula-based `dev_activity_score`.

### 1.3 Success criteria

| ID | Criterion | Measurement |
|----|-----------|-------------|
| S1 | All 3 new Bronze tables contain rows after first scheduled run | `SELECT COUNT(*) > 0` per table |
| S2 | `silver_asset_enriched` joins ≥ 50 % of top-100 CoinGecko assets to at least one enrichment column | row-level coverage metric |
| S3 | `silver_macro_context` returns ≥ 4 series with non-null `value` and `30d_change_pct` | row count by `series_id` |
| S4 | `gold_enriched_rankings`, `gold_defi_protocols`, `gold_macro_regime` are queryable by Genie via `ai_serving.mv_*` | live SQL validation passes |
| S5 | `validate_enrichment_chain.py` passes in CI | exit code 0 |
| S6 | No regression to Phase 1 chain | existing `validate_market_overview_chain.py` still passes |

### 1.4 Architectural alignment (CLAUDE.md rules)

- All new tables stored under Unity Catalog (`cgadev.market_bronze`, `cgadev.market_silver`, `cgadev.market_gold`, `cgadev.ai_serving`).
- All Genie-facing assets exposed strictly via `ai_serving.mv_*` views (no Bronze/Silver direct exposure).
- API keys via `dbutils.secrets.get()`; no PATs in code.
- Deployment via Databricks Asset Bundles; CI uses service principal (OAuth M2M).
- All Databricks/Terraform mutations remain behind manual approval gates (`workflow_dispatch`).

---

## 2. Data Flow Diagram

```text
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          PHASE 2 ENRICHMENT FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

     Phase 1 (existing, unchanged)
     ──────────────────────────────────────────────────────────────────
       CoinGecko API ──► bronze_market_snapshots ──► silver_market_*
                                                        │
                                                        ▼
                                              gold_market_rankings
                                                        │
                                                        ▼
                                                ai_serving.mv_market_rankings

     Phase 2 (new)
     ──────────────────────────────────────────────────────────────────
       DefiLlama API  ──► bronze_defillama_protocols ──┐
                          (every 6h, append)           │
                                                       │
       GitHub API     ──► bronze_github_activity   ────┤
       (+ asset_repo_map.json)                         │
       (every 6h, append)                              │
                                                       ▼
                                            silver_asset_enriched
                                            (join on asset_id/slug)
                                            (every 6h, append)
                                                       │
       FRED API       ──► bronze_fred_macro            │
                          (daily, append)              │
                                │                      │
                                ▼                      │
                          silver_macro_context         │
                          (daily, append)              │
                                │                      │
                                │                      ▼
                                │           gold_enriched_rankings
                                │           gold_defi_protocols
                                ▼           gold_macro_regime
                          ai_serving.mv_macro_regime
                          ai_serving.mv_enriched_rankings
                          ai_serving.mv_defi_protocols
                                │
                                ▼
                          AI/BI Genie (NLQ) + external frontend
```

### 2.1 Lineage summary

| Source | Bronze | Silver | Gold | ai_serving |
|--------|--------|--------|------|------------|
| DefiLlama | `bronze_defillama_protocols` | `silver_asset_enriched` | `gold_defi_protocols`, `gold_enriched_rankings` | `mv_defi_protocols`, `mv_enriched_rankings` |
| GitHub | `bronze_github_activity` | `silver_asset_enriched` | `gold_enriched_rankings` | `mv_enriched_rankings` |
| FRED | `bronze_fred_macro` | `silver_macro_context` | `gold_macro_regime` | `mv_macro_regime` |
| CoinGecko (Phase 1) | `bronze_market_snapshots` | `silver_*` | `gold_market_rankings`, fed into `gold_enriched_rankings` | `mv_market_rankings`, `mv_enriched_rankings` |

---

## 3. Schema Definitions

### 3.1 Bronze layer (`cgadev.market_bronze`)

#### 3.1.1 `bronze_defillama_protocols`

```sql
CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_defillama_protocols (
  source_system        STRING,           -- 'defillama_api'
  source_record_id     STRING,           -- '{slug}:{observed_at}'
  protocol_slug        STRING,           -- DefiLlama 'slug', e.g. 'uniswap'
  protocol_name        STRING,           -- 'Uniswap'
  asset_id             STRING,           -- best-effort match to CoinGecko id; nullable
  symbol               STRING,           -- protocol token symbol (UPPER); nullable
  category             STRING,           -- 'Dexes', 'Lending', 'Liquid Staking', etc.
  chain                STRING,           -- 'Ethereum', 'Multi-Chain', etc.
  tvl_usd              DECIMAL(38, 8),
  fees_24h_usd         DECIMAL(38, 8),
  fees_7d_usd          DECIMAL(38, 8),
  revenue_24h_usd      DECIMAL(38, 8),
  revenue_7d_usd       DECIMAL(38, 8),
  mcap_usd             DECIMAL(38, 8),   -- DefiLlama-reported mcap (cross-check)
  observed_at          TIMESTAMP,
  ingested_at          TIMESTAMP,
  payload_version      STRING            -- 'defillama_protocols_v1'
) USING DELTA;
```

#### 3.1.2 `bronze_github_activity`

```sql
CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_github_activity (
  source_system        STRING,           -- 'github_api'
  source_record_id     STRING,           -- '{owner}/{repo}:{observed_at}'
  asset_id             STRING,           -- CoinGecko asset_id (from map)
  owner                STRING,
  repo                 STRING,
  full_name            STRING,           -- '{owner}/{repo}'
  stars                BIGINT,
  forks                BIGINT,
  open_issues          BIGINT,
  watchers             BIGINT,
  default_branch       STRING,
  language             STRING,
  commits_4w           BIGINT,           -- sum of last 4 ISO weeks from /stats/commit_activity
  commits_12w          BIGINT,           -- sum of last 12 ISO weeks
  contributors_count   BIGINT,           -- nullable; from /contributors?per_page=1 link header
  created_at           TIMESTAMP,        -- repo creation
  pushed_at            TIMESTAMP,        -- repo last push
  observed_at          TIMESTAMP,
  ingested_at          TIMESTAMP,
  payload_version      STRING            -- 'github_activity_v1'
) USING DELTA;
```

#### 3.1.3 `bronze_fred_macro`

```sql
CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_fred_macro (
  source_system        STRING,           -- 'fred_api'
  source_record_id     STRING,           -- '{series_id}:{observation_date}'
  series_id            STRING,           -- 'DXY', 'DGS10', 'M2SL', 'CPIAUCSL'
  series_title         STRING,           -- 'U.S. Dollar Index', etc.
  observation_date     DATE,
  value                DECIMAL(38, 8),   -- raw FRED value; nullable when '.'
  units                STRING,           -- 'Index', 'Percent', 'Billions of Dollars', etc.
  frequency            STRING,           -- 'Daily', 'Monthly'
  observed_at          TIMESTAMP,        -- equals observation_date midnight UTC
  ingested_at          TIMESTAMP,
  payload_version      STRING            -- 'fred_observations_v1'
) USING DELTA;
```

### 3.2 Silver layer (`cgadev.market_silver`)

#### 3.2.1 `silver_asset_enriched`

```sql
CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_asset_enriched (
  asset_id              STRING,
  symbol                STRING,
  name                  STRING,
  observed_at           TIMESTAMP,
  window_id             STRING,                   -- DATE(observed_at) as 'YYYY-MM-DD'

  -- CoinGecko-sourced (echoed for downstream join convenience)
  market_cap_usd        DECIMAL(38, 8),
  price_usd             DECIMAL(38, 8),
  volume_24h_usd        DECIMAL(38, 8),
  market_cap_rank       BIGINT,

  -- DefiLlama-sourced
  defi_protocol_slug    STRING,
  defi_tvl_usd          DECIMAL(38, 8),
  fees_24h_usd          DECIMAL(38, 8),
  revenue_24h_usd       DECIMAL(38, 8),

  -- GitHub-sourced
  github_full_name      STRING,
  github_stars          BIGINT,
  github_forks          BIGINT,
  github_commits_4w     BIGINT,
  github_commits_12w    BIGINT,
  github_contributors   BIGINT,

  -- Computed
  dev_activity_score    DECIMAL(10, 4),           -- 0–100 normalized

  ingested_at           TIMESTAMP
) USING DELTA;
```

#### 3.2.2 `silver_macro_context`

```sql
CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_macro_context (
  series_id             STRING,
  series_title          STRING,
  observation_date      DATE,
  value                 DECIMAL(38, 8),
  value_30d_ago         DECIMAL(38, 8),
  change_30d_abs        DECIMAL(38, 8),
  change_30d_pct        DECIMAL(38, 8),
  units                 STRING,
  frequency             STRING,
  observed_at           TIMESTAMP,
  ingested_at           TIMESTAMP
) USING DELTA;
```

### 3.3 Gold layer (views in `cgadev.market_gold`)

| View | Purpose |
|------|---------|
| `gold_enriched_rankings` | `gold_market_rankings` enriched with TVL, fees, dev score |
| `gold_defi_protocols` | DeFi-only ranking by TVL/fees/revenue |
| `gold_macro_regime` | Latest FRED observation per series with regime label |

(Full `CREATE OR REPLACE VIEW` definitions in §5.)

### 3.4 ai_serving layer (views in `cgadev.ai_serving`)

| View | Source |
|------|--------|
| `mv_enriched_rankings` | `cgadev.market_gold.gold_enriched_rankings` |
| `mv_defi_protocols` | `cgadev.market_gold.gold_defi_protocols` |
| `mv_macro_regime` | `cgadev.market_gold.gold_macro_regime` |

---

## 4. Job Specifications

All jobs follow the established pattern:

- Pure-Python file under `databricks/jobs/`.
- Uses the runtime-injected `spark` session at the `__main__` guard.
- Reads widgets via `dbutils.widgets.get(...)` with try/except fallback.
- Reads secrets via `dbutils.secrets.get(scope, key)` with `os.environ` fallback for tests.
- Uses `urllib.request` only (no extra dependencies — keeps `environments.dependencies = []`).
- Bronze writes use `mode("append").format("delta").saveAsTable(full_table_name)`.
- All structured payload normalization happens in pure functions that accept a `dict` and return a `dict`, so they're unit-testable without Spark.

### 4.1 `defillama_ingestion_job`

| Field | Value |
|-------|-------|
| File | `databricks/jobs/defillama_ingestion_job.py` |
| Target | `cgadev.market_bronze.bronze_defillama_protocols` |
| Mode | append, Delta |
| Schedule | `0 0 */6 * * ?` (every 6 h) America/Sao_Paulo |
| Secret | none (DefiLlama is unauthenticated) |
| Test | `databricks/tests/test_defillama_ingestion_job.py` |

**API calls:**

1. `GET https://api.llama.fi/protocols` → list of `{name, slug, gecko_id, symbol, category, chains, tvl, mcap}`.
2. For top-N by TVL (default `N = 200`), `GET https://api.llama.fi/summary/fees/{slug}?dataType=dailyFees` and `dataType=dailyRevenue`. (One pass; cap N to bound runtime.)

**Normalization:**

- `protocol_slug` ← `slug`.
- `asset_id` ← `gecko_id` (DefiLlama already provides this mapping).
- `tvl_usd` ← `tvl` (sum of all chains).
- `fees_24h_usd`, `fees_7d_usd`, `revenue_24h_usd`, `revenue_7d_usd` extracted from `total24h`, `total7d` of fees/revenue summary.
- `observed_at` ← `_utc_now_isoformat()` truncated to 6 h grid (`floor_to_6h(now_utc)`) so consecutive runs within the same window deduplicate cleanly.
- `source_record_id` ← `f"{slug}:{observed_at}"`.

**Error handling:**

- Reuse the retry pattern from `market_source_ingestion_job._request_json_with_retry` (max 3 attempts on 429/5xx with linear backoff).
- On per-protocol fees/revenue 404 (some protocols don't expose them), set fields to `NULL` and continue.
- A single non-recoverable error fails the whole job (better to fail loudly than partially load).

**Inputs / Outputs:**

- Inputs: optional widgets `payload_path` (for fixture-driven tests) and `target_table`.
- Outputs: stdout JSON `{"rows_written": N, "target_table": "..."}` (matches Phase 1 contract).

### 4.2 `github_activity_ingestion_job`

| Field | Value |
|-------|-------|
| File | `databricks/jobs/github_activity_ingestion_job.py` |
| Config | `databricks/config/github_asset_repo_map.json` |
| Target | `cgadev.market_bronze.bronze_github_activity` |
| Mode | append, Delta |
| Schedule | `0 30 */6 * * ?` (every 6 h, offset 30 min from DefiLlama) |
| Secret | optional `dbutils.secrets.get("github", "token")`; raises rate limit from 60/h to 5000/h |
| Test | `databricks/tests/test_github_activity_ingestion_job.py` |

**API calls (per repo in map):**

1. `GET https://api.github.com/repos/{owner}/{repo}` → stars, forks, watchers, language, default_branch, created_at, pushed_at.
2. `GET https://api.github.com/repos/{owner}/{repo}/stats/commit_activity` → 52 weeks of `{total, week, days}`. Sum `total` over last 4 and 12 entries.
3. `GET https://api.github.com/repos/{owner}/{repo}/contributors?per_page=1&anon=true` → parse `Link: <...&page=N>; rel="last"` to extract contributor count without paginating.

**Headers:**

```python
headers = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
    "User-Agent": "coingeckoanalytical-bot",
}
if token:
    headers["Authorization"] = f"Bearer {token}"
```

**Normalization:**

- `asset_id` ← key from map.
- `commits_4w` ← `sum(weeks[-4:].total)`; `commits_12w` ← `sum(weeks[-12:].total)`.
- If `/stats/commit_activity` returns HTTP 202 (GitHub computing), retry once after 5 s sleep; on second 202 set commits to `NULL`.
- `observed_at` floored to 6 h grid (same as DefiLlama).

**Error handling:**

- 403 with `X-RateLimit-Remaining: 0` → log and skip remaining repos in this run (no retry; next 6 h window is fine).
- 404 → log and skip that repo.
- 5xx → retry up to 3 with linear backoff (reuse helper).

**Asset–repo map (`databricks/config/github_asset_repo_map.json`):**

```json
{
  "version": 1,
  "updated_at": "2026-05-02",
  "mappings": [
    { "asset_id": "bitcoin",     "owner": "bitcoin",          "repo": "bitcoin" },
    { "asset_id": "ethereum",    "owner": "ethereum",         "repo": "go-ethereum" },
    { "asset_id": "solana",      "owner": "solana-labs",      "repo": "solana" },
    { "asset_id": "uniswap",     "owner": "Uniswap",          "repo": "v3-core" },
    { "asset_id": "aave",        "owner": "aave",             "repo": "aave-v3-core" },
    { "asset_id": "chainlink",   "owner": "smartcontractkit", "repo": "chainlink" },
    { "asset_id": "cosmos",      "owner": "cosmos",           "repo": "cosmos-sdk" },
    { "asset_id": "polkadot",    "owner": "paritytech",       "repo": "polkadot-sdk" },
    { "asset_id": "avalanche-2", "owner": "ava-labs",         "repo": "avalanchego" },
    { "asset_id": "near",        "owner": "near",             "repo": "nearcore" },
    { "asset_id": "polygon-pos", "owner": "0xPolygon",        "repo": "polygon-edge" },
    { "asset_id": "arbitrum",    "owner": "OffchainLabs",     "repo": "nitro" },
    { "asset_id": "optimism",    "owner": "ethereum-optimism","repo": "optimism" },
    { "asset_id": "the-graph",   "owner": "graphprotocol",    "repo": "graph-node" },
    { "asset_id": "lido-dao",    "owner": "lidofinance",      "repo": "lido-dao" },
    { "asset_id": "curve-dao-token","owner": "curvefi",       "repo": "curve-contract" },
    { "asset_id": "maker",       "owner": "makerdao",         "repo": "dss" },
    { "asset_id": "compound-governance-token","owner": "compound-finance","repo": "compound-protocol" },
    { "asset_id": "filecoin",    "owner": "filecoin-project", "repo": "lotus" },
    { "asset_id": "litecoin",    "owner": "litecoin-project", "repo": "litecoin" }
  ]
}
```

The map is **versioned**, **bounded** (≤ 50 entries to fit a single 6 h GitHub anonymous-rate-limit window), and **hot-reloadable** (the job re-reads on each run). Adding entries is a PR-only operation.

### 4.3 `fred_macro_ingestion_job`

| Field | Value |
|-------|-------|
| File | `databricks/jobs/fred_macro_ingestion_job.py` |
| Target | `cgadev.market_bronze.bronze_fred_macro` |
| Mode | append, Delta |
| Schedule | `0 0 7 * * ?` (daily 07:00 America/Sao_Paulo) |
| Secret | required `dbutils.secrets.get("fred", "api_key")` |
| Test | `databricks/tests/test_fred_macro_ingestion_job.py` |

**Series fetched (config table inside the job module):**

```python
FRED_SERIES = (
    {"series_id": "DXY",      "title": "U.S. Dollar Index",            "units": "Index",                "frequency": "Daily"},
    {"series_id": "DGS10",    "title": "10-Year Treasury Yield",       "units": "Percent",              "frequency": "Daily"},
    {"series_id": "M2SL",     "title": "M2 Money Stock",               "units": "Billions of Dollars",  "frequency": "Monthly"},
    {"series_id": "CPIAUCSL", "title": "CPI All Urban Consumers",      "units": "Index 1982-1984=100",  "frequency": "Monthly"},
)
```

**API call (per series):**

```
GET https://api.stlouisfed.org/fred/series/observations
    ?series_id={series_id}
    &api_key={key}
    &file_type=json
    &observation_start={today - 400 days}
    &observation_end={today}
```

400 days of lookback ensures the 30-day-change calculation always has a comparison row even on long weekends / holidays.

**Normalization:**

- Skip rows where `value == "."` (FRED's missing-value sentinel).
- `observation_date` ← `date(value)` parsed from `YYYY-MM-DD`.
- `observed_at` ← `observation_date` at midnight UTC (so Bronze can be partition-pruned by `observed_at` like everything else).
- `source_record_id` ← `f"{series_id}:{observation_date}"`.

**Idempotency:**

Bronze is append-only, but `silver_macro_context` and downstream views deduplicate on `(series_id, observation_date)`, so daily reruns that re-fetch overlapping windows are safe.

**Error handling:**

- HTTP 400 with `error_code=400` and message about invalid `api_key` → fail fast (config bug).
- 5xx → retry up to 3 times with linear backoff.
- Per-series error → fail fast (only 4 series, no point partial-loading).

### 4.4 `silver_enrichment_pipeline_job`

| Field | Value |
|-------|-------|
| File | `databricks/jobs/silver_enrichment_pipeline_job.py` |
| Targets | `cgadev.market_silver.silver_asset_enriched`, `cgadev.market_silver.silver_macro_context` |
| Mode | append, Delta |
| Schedule | `0 45 */6 * * ?` (every 6 h, 45 min offset to ensure DefiLlama + GitHub Bronze writes have committed) |
| Test | `databricks/tests/test_silver_enrichment_pipeline_job.py` |

**Logic — `silver_asset_enriched`:**

```sql
WITH cg_latest AS (
  SELECT
    asset_id, symbol, name, observed_at, market_cap_usd, price_usd,
    volume_24h_usd, market_cap_rank, ingested_at,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id
      ORDER BY observed_at DESC, ingested_at DESC
    ) AS rn
  FROM cgadev.market_bronze.bronze_market_snapshots
  WHERE observed_at >= current_timestamp() - INTERVAL 24 HOURS
),
defi_latest AS (
  SELECT
    asset_id, protocol_slug, tvl_usd, fees_24h_usd, revenue_24h_usd,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id
      ORDER BY observed_at DESC, ingested_at DESC
    ) AS rn
  FROM cgadev.market_bronze.bronze_defillama_protocols
  WHERE asset_id IS NOT NULL
    AND observed_at >= current_timestamp() - INTERVAL 24 HOURS
),
gh_latest AS (
  SELECT
    asset_id, full_name AS github_full_name, stars, forks,
    commits_4w, commits_12w, contributors_count,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id
      ORDER BY observed_at DESC, ingested_at DESC
    ) AS rn
  FROM cgadev.market_bronze.bronze_github_activity
  WHERE observed_at >= current_timestamp() - INTERVAL 24 HOURS
),
gh_max AS (
  SELECT
    MAX(stars)        AS max_stars,
    MAX(commits_12w)  AS max_commits_12w
  FROM gh_latest WHERE rn = 1
)
SELECT
  c.asset_id,
  UPPER(c.symbol) AS symbol,
  c.name,
  c.observed_at,
  CAST(DATE(c.observed_at) AS STRING) AS window_id,
  c.market_cap_usd,
  c.price_usd,
  c.volume_24h_usd,
  c.market_cap_rank,
  d.protocol_slug                 AS defi_protocol_slug,
  d.tvl_usd                       AS defi_tvl_usd,
  d.fees_24h_usd,
  d.revenue_24h_usd,
  g.github_full_name,
  g.stars                         AS github_stars,
  g.forks                         AS github_forks,
  g.commits_4w                    AS github_commits_4w,
  g.commits_12w                   AS github_commits_12w,
  g.contributors_count            AS github_contributors,
  -- dev_activity_score in [0, 100]:
  --   0.4 * normalized commits_12w + 0.3 * normalized stars + 0.3 * normalized contributors
  CAST(
    100 * (
      0.4 * COALESCE(g.commits_12w, 0)        / NULLIF((SELECT max_commits_12w FROM gh_max), 0)
    + 0.3 * COALESCE(g.stars, 0)              / NULLIF((SELECT max_stars FROM gh_max), 0)
    + 0.3 * LEAST(COALESCE(g.contributors_count, 0), 1000) / 1000.0
    ) AS DECIMAL(10, 4)
  ) AS dev_activity_score,
  current_timestamp() AS ingested_at
FROM cg_latest c
  LEFT JOIN defi_latest d ON d.rn = 1 AND c.rn = 1 AND d.asset_id = c.asset_id
  LEFT JOIN gh_latest g   ON g.rn = 1 AND c.rn = 1 AND g.asset_id = c.asset_id
WHERE c.rn = 1;
```

`dev_activity_score` notes:
- Normalization is **batch-relative** (max within current run), so the score is comparable across assets in the same window but not across runs.
- Contributors capped at 1000 to avoid extreme outliers (Bitcoin Core has ~900, Ethereum has ~800, vs. small protocols at <30).
- For assets with no GitHub mapping, score is `0.0` rather than `NULL` so Genie aggregations don't drop them silently.

**Logic — `silver_macro_context`:**

```sql
WITH ranked AS (
  SELECT
    series_id, series_title, observation_date, value, units, frequency,
    observed_at, ingested_at,
    ROW_NUMBER() OVER (
      PARTITION BY series_id, observation_date
      ORDER BY ingested_at DESC, source_record_id DESC
    ) AS rn
  FROM cgadev.market_bronze.bronze_fred_macro
  WHERE value IS NOT NULL
),
deduped AS (
  SELECT * FROM ranked WHERE rn = 1
),
with_lag AS (
  SELECT
    series_id, series_title, observation_date, value, units, frequency,
    observed_at,
    -- pick the value from ~30 days ago (LAG by date, not row)
    (
      SELECT value FROM deduped d2
      WHERE d2.series_id = d1.series_id
        AND d2.observation_date <= d1.observation_date - INTERVAL 30 DAYS
      ORDER BY d2.observation_date DESC
      LIMIT 1
    ) AS value_30d_ago
  FROM deduped d1
)
SELECT
  series_id,
  series_title,
  observation_date,
  CAST(value AS DECIMAL(38, 8)) AS value,
  CAST(value_30d_ago AS DECIMAL(38, 8)) AS value_30d_ago,
  CAST(value - value_30d_ago AS DECIMAL(38, 8)) AS change_30d_abs,
  CASE
    WHEN value_30d_ago IS NULL OR value_30d_ago = 0 THEN NULL
    ELSE CAST(((value - value_30d_ago) / value_30d_ago) * 100 AS DECIMAL(38, 8))
  END AS change_30d_pct,
  units,
  frequency,
  observed_at,
  current_timestamp() AS ingested_at
FROM with_lag;
```

**Outputs:** stdout JSON
```json
{
  "asset_enriched_rows_written": N1,
  "macro_context_rows_written": N2,
  "asset_enriched_target_table": "cgadev.market_silver.silver_asset_enriched",
  "macro_context_target_table": "cgadev.market_silver.silver_macro_context"
}
```

### 4.5 Migration jobs

#### 4.5.1 `bronze_enrichment_table_migration_job`

| Field | Value |
|-------|-------|
| File | `databricks/jobs/bronze_enrichment_table_migration_job.py` |
| SQL | `databricks/sql/migrations/bronze_enrichment_migration.sql` |
| Test | `databricks/tests/test_bronze_enrichment_table_migration_job.py` |

Same structure as `bronze_market_table_migration_job.py`: loads SQL statements, executes each via `spark.sql()`. Provisions all three new Bronze tables.

#### 4.5.2 `silver_enrichment_table_migration_job`

| Field | Value |
|-------|-------|
| File | `databricks/jobs/silver_enrichment_table_migration_job.py` |
| SQL | `databricks/sql/migrations/silver_enrichment_migration.sql` |
| Test | `databricks/tests/test_silver_enrichment_table_migration_job.py` |

Same structure as `silver_market_migration_job.py` (drops conflicting views before recreating, supports `CREATE TABLE IF NOT EXISTS`).

---

## 5. SQL View Definitions

### 5.1 New migration files

**`databricks/sql/migrations/bronze_enrichment_migration.sql`**

```sql
-- Bronze Enrichment Migration
-- Provisions Bronze landing tables for DefiLlama / GitHub / FRED.

CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_defillama_protocols (
  source_system STRING,
  source_record_id STRING,
  protocol_slug STRING,
  protocol_name STRING,
  asset_id STRING,
  symbol STRING,
  category STRING,
  chain STRING,
  tvl_usd DECIMAL(38, 8),
  fees_24h_usd DECIMAL(38, 8),
  fees_7d_usd DECIMAL(38, 8),
  revenue_24h_usd DECIMAL(38, 8),
  revenue_7d_usd DECIMAL(38, 8),
  mcap_usd DECIMAL(38, 8),
  observed_at TIMESTAMP,
  ingested_at TIMESTAMP,
  payload_version STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_github_activity (
  source_system STRING,
  source_record_id STRING,
  asset_id STRING,
  owner STRING,
  repo STRING,
  full_name STRING,
  stars BIGINT,
  forks BIGINT,
  open_issues BIGINT,
  watchers BIGINT,
  default_branch STRING,
  language STRING,
  commits_4w BIGINT,
  commits_12w BIGINT,
  contributors_count BIGINT,
  created_at TIMESTAMP,
  pushed_at TIMESTAMP,
  observed_at TIMESTAMP,
  ingested_at TIMESTAMP,
  payload_version STRING
) USING DELTA;

CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_fred_macro (
  source_system STRING,
  source_record_id STRING,
  series_id STRING,
  series_title STRING,
  observation_date DATE,
  value DECIMAL(38, 8),
  units STRING,
  frequency STRING,
  observed_at TIMESTAMP,
  ingested_at TIMESTAMP,
  payload_version STRING
) USING DELTA;
```

**`databricks/sql/migrations/silver_enrichment_migration.sql`**

```sql
-- Silver Enrichment Migration
-- Provisions Silver Delta tables for the enrichment chain.

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_asset_enriched (
  asset_id STRING,
  symbol STRING,
  name STRING,
  observed_at TIMESTAMP,
  window_id STRING,
  market_cap_usd DECIMAL(38, 8),
  price_usd DECIMAL(38, 8),
  volume_24h_usd DECIMAL(38, 8),
  market_cap_rank BIGINT,
  defi_protocol_slug STRING,
  defi_tvl_usd DECIMAL(38, 8),
  fees_24h_usd DECIMAL(38, 8),
  revenue_24h_usd DECIMAL(38, 8),
  github_full_name STRING,
  github_stars BIGINT,
  github_forks BIGINT,
  github_commits_4w BIGINT,
  github_commits_12w BIGINT,
  github_contributors BIGINT,
  dev_activity_score DECIMAL(10, 4),
  ingested_at TIMESTAMP
) USING DELTA;

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_macro_context (
  series_id STRING,
  series_title STRING,
  observation_date DATE,
  value DECIMAL(38, 8),
  value_30d_ago DECIMAL(38, 8),
  change_30d_abs DECIMAL(38, 8),
  change_30d_pct DECIMAL(38, 8),
  units STRING,
  frequency STRING,
  observed_at TIMESTAMP,
  ingested_at TIMESTAMP
) USING DELTA;
```

### 5.2 Gold views (`databricks/sql/layers/gold_enrichment_views.sql`)

```sql
-- Gold Enrichment Views
-- Purpose: governed analytical surfaces for enriched market intelligence.

CREATE OR REPLACE VIEW cgadev.market_gold.gold_enriched_rankings AS
WITH base AS (
  SELECT
    r.asset_id,
    r.symbol,
    r.name,
    r.category,
    r.observed_at,
    r.market_cap_usd,
    r.price_usd,
    r.volume_24h_usd,
    r.market_cap_rank,
    e.defi_tvl_usd,
    e.fees_24h_usd,
    e.revenue_24h_usd,
    e.github_stars,
    e.github_commits_12w,
    e.github_contributors,
    e.dev_activity_score
  FROM cgadev.market_gold.gold_market_rankings r
  LEFT JOIN cgadev.market_silver.silver_asset_enriched e
    ON e.asset_id = r.asset_id
   AND e.observed_at = r.observed_at
)
SELECT
  asset_id,
  symbol,
  name,
  category,
  observed_at,
  market_cap_usd,
  price_usd,
  volume_24h_usd,
  market_cap_rank,
  defi_tvl_usd,
  fees_24h_usd,
  revenue_24h_usd,
  github_stars,
  github_commits_12w,
  github_contributors,
  COALESCE(dev_activity_score, 0.0) AS dev_activity_score,
  CASE
    WHEN defi_tvl_usd IS NOT NULL  THEN 'tracked'
    ELSE 'not_tracked'
  END AS defi_coverage,
  CASE
    WHEN github_stars IS NOT NULL  THEN 'tracked'
    ELSE 'not_tracked'
  END AS github_coverage,
  'tier_b' AS freshness_tier,
  360 AS freshness_target_minutes,
  'silver_asset_enriched' AS lineage_source,
  CASE
    WHEN market_cap_usd >= 0 AND price_usd >= 0 THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM base;

CREATE OR REPLACE VIEW cgadev.market_gold.gold_defi_protocols AS
WITH ranked AS (
  SELECT
    asset_id,
    symbol,
    name,
    defi_protocol_slug,
    observed_at,
    market_cap_usd,
    defi_tvl_usd,
    fees_24h_usd,
    revenue_24h_usd,
    CASE
      WHEN defi_tvl_usd IS NULL OR defi_tvl_usd = 0 THEN NULL
      ELSE market_cap_usd / defi_tvl_usd
    END AS mcap_to_tvl_ratio,
    CASE
      WHEN defi_tvl_usd IS NULL OR defi_tvl_usd = 0 THEN NULL
      ELSE (fees_24h_usd * 365) / defi_tvl_usd
    END AS fees_to_tvl_apr,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id
      ORDER BY observed_at DESC
    ) AS rn
  FROM cgadev.market_silver.silver_asset_enriched
  WHERE defi_tvl_usd IS NOT NULL AND defi_tvl_usd > 0
)
SELECT
  asset_id,
  symbol,
  name,
  defi_protocol_slug,
  observed_at,
  market_cap_usd,
  defi_tvl_usd,
  fees_24h_usd,
  revenue_24h_usd,
  mcap_to_tvl_ratio,
  fees_to_tvl_apr,
  RANK() OVER (ORDER BY defi_tvl_usd DESC) AS tvl_rank,
  RANK() OVER (ORDER BY COALESCE(fees_24h_usd, 0) DESC) AS fees_rank,
  RANK() OVER (ORDER BY COALESCE(revenue_24h_usd, 0) DESC) AS revenue_rank,
  'tier_b' AS freshness_tier,
  360 AS freshness_target_minutes,
  'silver_asset_enriched' AS lineage_source,
  'pass' AS quality_status
FROM ranked
WHERE rn = 1;

CREATE OR REPLACE VIEW cgadev.market_gold.gold_macro_regime AS
WITH ranked AS (
  SELECT
    series_id,
    series_title,
    observation_date,
    value,
    value_30d_ago,
    change_30d_abs,
    change_30d_pct,
    units,
    frequency,
    observed_at,
    ROW_NUMBER() OVER (
      PARTITION BY series_id
      ORDER BY observation_date DESC
    ) AS rn
  FROM cgadev.market_silver.silver_macro_context
)
SELECT
  series_id,
  series_title AS series_name,
  observation_date,
  value AS current_value,
  value_30d_ago,
  change_30d_abs,
  change_30d_pct AS change_30d_pct,
  units,
  frequency,
  CASE series_id
    WHEN 'DXY' THEN
      CASE
        WHEN change_30d_pct >  2 THEN 'usd_strengthening'
        WHEN change_30d_pct < -2 THEN 'usd_weakening'
        ELSE 'usd_neutral'
      END
    WHEN 'DGS10' THEN
      CASE
        WHEN change_30d_abs >  0.30 THEN 'rates_rising'
        WHEN change_30d_abs < -0.30 THEN 'rates_falling'
        ELSE 'rates_stable'
      END
    WHEN 'M2SL' THEN
      CASE
        WHEN change_30d_pct >  0.5 THEN 'liquidity_expanding'
        WHEN change_30d_pct < -0.5 THEN 'liquidity_contracting'
        ELSE 'liquidity_stable'
      END
    WHEN 'CPIAUCSL' THEN
      CASE
        WHEN change_30d_pct >  0.4 THEN 'inflation_accelerating'
        WHEN change_30d_pct < -0.1 THEN 'disinflation'
        ELSE 'inflation_steady'
      END
    ELSE 'unclassified'
  END AS regime_label,
  'tier_c' AS freshness_tier,
  1440 AS freshness_target_minutes,
  'silver_macro_context' AS lineage_source,
  CASE
    WHEN value IS NOT NULL THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM ranked
WHERE rn = 1;
```

### 5.3 ai_serving views (append to `databricks/sql/layers/genie_metric_views.sql`)

```sql
-- Phase 2 enrichment metric views (append to existing file)

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_enriched_rankings AS
SELECT * FROM cgadev.market_gold.gold_enriched_rankings;

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_defi_protocols AS
SELECT * FROM cgadev.market_gold.gold_defi_protocols;

CREATE OR REPLACE VIEW cgadev.ai_serving.mv_macro_regime AS
SELECT * FROM cgadev.market_gold.gold_macro_regime;
```

---

## 6. Bundle Config Additions (`databricks/databricks.yml`)

Append the following blocks under `resources.jobs:` (Phase 1 jobs unchanged):

```yaml
    bronze_enrichment_table_migration_job:
      name: bronze_enrichment_table_migration_job
      description: Provision Bronze enrichment tables (DefiLlama, GitHub, FRED).
      tasks:
        - task_key: migrate_bronze_enrichment_tables
          spark_python_task:
            python_file: ./jobs/bronze_enrichment_table_migration_job.py
          environment_key: default
      environments:
        - environment_key: default
          spec:
            environment_version: "2"
            dependencies: []

    silver_enrichment_table_migration_job:
      name: silver_enrichment_table_migration_job
      description: Provision Silver enrichment tables (asset_enriched, macro_context).
      tasks:
        - task_key: migrate_silver_enrichment_tables
          spark_python_task:
            python_file: ./jobs/silver_enrichment_table_migration_job.py
          environment_key: default
      environments:
        - environment_key: default
          spec:
            environment_version: "2"
            dependencies: []

    defillama_ingestion_job:
      name: defillama_ingestion_job
      description: Append normalized DefiLlama protocol metrics into bronze_defillama_protocols.
      tasks:
        - task_key: ingest_defillama_protocols
          spark_python_task:
            python_file: ./jobs/defillama_ingestion_job.py
          environment_key: default
      schedule:
        quartz_cron_expression: "0 0 */6 * * ?"
        timezone_id: America/Sao_Paulo
        pause_status: UNPAUSED
      environments:
        - environment_key: default
          spec:
            environment_version: "2"
            dependencies: []

    github_activity_ingestion_job:
      name: github_activity_ingestion_job
      description: Append GitHub repo activity metrics for tracked assets into bronze_github_activity.
      tasks:
        - task_key: ingest_github_activity
          spark_python_task:
            python_file: ./jobs/github_activity_ingestion_job.py
          environment_key: default
      schedule:
        quartz_cron_expression: "0 30 */6 * * ?"
        timezone_id: America/Sao_Paulo
        pause_status: UNPAUSED
      environments:
        - environment_key: default
          spec:
            environment_version: "2"
            dependencies: []

    fred_macro_ingestion_job:
      name: fred_macro_ingestion_job
      description: Append FRED macro series observations into bronze_fred_macro.
      tasks:
        - task_key: ingest_fred_macro
          spark_python_task:
            python_file: ./jobs/fred_macro_ingestion_job.py
          environment_key: default
      schedule:
        quartz_cron_expression: "0 0 7 * * ?"
        timezone_id: America/Sao_Paulo
        pause_status: UNPAUSED
      environments:
        - environment_key: default
          spec:
            environment_version: "2"
            dependencies: []

    silver_enrichment_pipeline_job:
      name: silver_enrichment_pipeline_job
      description: Materialise Silver enrichment tables (silver_asset_enriched, silver_macro_context).
      tasks:
        - task_key: run_silver_enrichment_pipeline
          spark_python_task:
            python_file: ./jobs/silver_enrichment_pipeline_job.py
          environment_key: default
      schedule:
        quartz_cron_expression: "0 45 */6 * * ?"
        timezone_id: America/Sao_Paulo
        pause_status: UNPAUSED
      environments:
        - environment_key: default
          spec:
            environment_version: "2"
            dependencies: []
```

The `sync.exclude` list does **not** need changes — `databricks/config/github_asset_repo_map.json` is intended to be deployed, not excluded.

---

## 7. CI/CD Additions

### 7.1 New tools

| File | Purpose |
|------|---------|
| `databricks/tools/validate_enrichment_chain.py` | Mirrors `validate_market_overview_chain.py` but checks Phase 2 SQL/job objects |

**`validate_enrichment_chain.py` expectations:**

```python
EXPECTED_BRONZE_OBJECTS = {
    "bronze_defillama_protocols":  "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_defillama_protocols",
    "bronze_github_activity":      "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_github_activity",
    "bronze_fred_macro":           "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_fred_macro",
}
EXPECTED_SILVER_OBJECTS = {
    "silver_asset_enriched": "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_asset_enriched",
    "silver_macro_context":  "CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_macro_context",
}
EXPECTED_GOLD_OBJECTS = {
    "gold_enriched_rankings": "CREATE OR REPLACE VIEW cgadev.market_gold.gold_enriched_rankings AS",
    "gold_defi_protocols":    "CREATE OR REPLACE VIEW cgadev.market_gold.gold_defi_protocols AS",
    "gold_macro_regime":      "CREATE OR REPLACE VIEW cgadev.market_gold.gold_macro_regime AS",
}
EXPECTED_METRIC_VIEWS = {
    "mv_enriched_rankings": "FROM cgadev.market_gold.gold_enriched_rankings",
    "mv_defi_protocols":    "FROM cgadev.market_gold.gold_defi_protocols",
    "mv_macro_regime":      "FROM cgadev.market_gold.gold_macro_regime",
}
DEPENDENCY_CHECKS = (
    ("gold_enriched_rankings", "FROM cgadev.market_gold.gold_market_rankings",  gold_sql),
    ("gold_enriched_rankings", "JOIN cgadev.market_silver.silver_asset_enriched", gold_sql),
    ("gold_defi_protocols",    "FROM cgadev.market_silver.silver_asset_enriched", gold_sql),
    ("gold_macro_regime",      "FROM cgadev.market_silver.silver_macro_context",  gold_sql),
)
LINEAGE_EXPECTATIONS = (
    "`DefiLlama API`", "`GitHub API`", "`FRED API`",
    "`market_bronze.bronze_defillama_protocols`",
    "`market_bronze.bronze_github_activity`",
    "`market_bronze.bronze_fred_macro`",
    "`market_silver.silver_asset_enriched`",
    "`market_silver.silver_macro_context`",
    "`market_gold.gold_enriched_rankings`",
    "`market_gold.gold_defi_protocols`",
    "`market_gold.gold_macro_regime`",
    "`ai_serving.mv_enriched_rankings`",
    "`ai_serving.mv_defi_protocols`",
    "`ai_serving.mv_macro_regime`",
)
ASSET_REPO_MAP_EXPECTATIONS = ("ethereum", "uniswap", "bitcoin", "solana")
```

The tool also asserts that `databricks/config/github_asset_repo_map.json` exists, parses as JSON, contains `version >= 1`, and has at least 10 mappings each with non-empty `asset_id`/`owner`/`repo`.

### 7.2 New tests

Under `databricks/tests/`:

| Test file | Coverage |
|-----------|----------|
| `test_defillama_ingestion_job.py` | normalize, dedup, retry, fixture-driven write |
| `test_github_activity_ingestion_job.py` | header parsing for contributor count, commit-activity sum, 202 retry |
| `test_fred_macro_ingestion_job.py` | `.` skip, normalization, idempotent reruns |
| `test_silver_enrichment_pipeline_job.py` | join behavior, dev_activity_score formula, NULL handling |
| `test_bronze_enrichment_table_migration_job.py` | SQL load + statement count |
| `test_silver_enrichment_table_migration_job.py` | drop-views-then-create flow |
| `test_validate_enrichment_chain.py` | the new validator catches removed objects/dependencies |

Under `databricks/fixtures/`:

| Fixture | Purpose |
|---------|---------|
| `defillama_protocols_sample.json` | 10 representative protocol records |
| `github_repo_sample.json` | 1 repo response + 1 commit_activity response + 1 contributors link header |
| `fred_observations_sample.json` | 60 daily DGS10 observations covering 30 d-back lag |

### 7.3 `ci.yml` additions

Add to the `contract` job's `Run Databricks helper tests` step (alphabetical insert):

```yaml
          python3 -m unittest databricks.tests.test_defillama_ingestion_job
          python3 -m unittest databricks.tests.test_github_activity_ingestion_job
          python3 -m unittest databricks.tests.test_fred_macro_ingestion_job
          python3 -m unittest databricks.tests.test_silver_enrichment_pipeline_job
          python3 -m unittest databricks.tests.test_bronze_enrichment_table_migration_job
          python3 -m unittest databricks.tests.test_silver_enrichment_table_migration_job
          python3 -m unittest databricks.tests.test_validate_enrichment_chain
```

Add a new step after `Run market overview chain validation`:

```yaml
      - name: Run enrichment chain validation
        run: python3 databricks/tools/validate_enrichment_chain.py
```

In the `deploy` job, append to the `Deploy bundle` step (after the existing `databricks bundle run …` lines, **before** the `Run live SQL validation` step):

```bash
          databricks bundle run bronze_enrichment_table_migration_job -t dev
          databricks bundle run silver_enrichment_table_migration_job -t dev
          DEFILLAMA_PAYLOAD_JSON=$(python3 -c 'import json, pathlib; print(json.dumps(json.loads(pathlib.Path("databricks/fixtures/defillama_protocols_sample.json").read_text(encoding="utf-8")), separators=(",", ":")))')
          FRED_PAYLOAD_JSON=$(python3 -c 'import json, pathlib; print(json.dumps(json.loads(pathlib.Path("databricks/fixtures/fred_observations_sample.json").read_text(encoding="utf-8")), separators=(",", ":")))')
          databricks bundle run defillama_ingestion_job        -t dev -- --payload-json "$DEFILLAMA_PAYLOAD_JSON"
          databricks bundle run github_activity_ingestion_job  -t dev -- --skip-live   # honors GITHUB_TOKEN absence in CI
          databricks bundle run fred_macro_ingestion_job       -t dev -- --payload-json "$FRED_PAYLOAD_JSON"
          databricks bundle run silver_enrichment_pipeline_job -t dev
```

Each ingestion job must accept a `--skip-live` flag (widget + CLI arg) that skips outbound HTTP and is a no-op write — this is what makes the deploy step deterministic in CI when secrets are absent.

`live_sql_validation.py` (existing) gets three new probe queries appended:

```sql
SELECT COUNT(*) FROM cgadev.ai_serving.mv_enriched_rankings;
SELECT COUNT(*) FROM cgadev.ai_serving.mv_defi_protocols;
SELECT COUNT(*) FROM cgadev.ai_serving.mv_macro_regime;
```

### 7.4 Secret provisioning

Update `.github/workflows/setup-databricks-secrets.yml` (or follow-up PR) to ensure the following scopes/keys exist in dev/staging/prod:

| Scope | Key | Required by |
|-------|-----|-------------|
| `fred` | `api_key` | `fred_macro_ingestion_job` |
| `github` | `token` | `github_activity_ingestion_job` (optional but strongly recommended) |

Both follow the existing `coingecko/api_key` pattern. Service principal must have `READ` on these scopes.

### 7.5 Approval gates (CLAUDE.md compliance)

The Phase 2 deploy steps run only when `workflow_dispatch.inputs.confirm_deploy == true`, identical to Phase 1. Update `.agentcodex/ops/approval-gate-policy.md` to enumerate the six new jobs as Databricks-mutation surfaces requiring chat approval before any `databricks bundle run` invocation.

### 7.6 Lineage map

Append a new section to `databricks/unity-catalog-lineage-map.md`:

```text
### Phase 2 Enrichment

`DefiLlama API` ──► `market_bronze.bronze_defillama_protocols` ──┐
`GitHub API`    ──► `market_bronze.bronze_github_activity`     ──┼──► `market_silver.silver_asset_enriched` ──► `market_gold.gold_enriched_rankings` ──► `ai_serving.mv_enriched_rankings`
`CoinGecko API` ──► `market_bronze.bronze_market_snapshots`    ──┘                                          ──► `market_gold.gold_defi_protocols`    ──► `ai_serving.mv_defi_protocols`

`FRED API`      ──► `market_bronze.bronze_fred_macro` ──► `market_silver.silver_macro_context` ──► `market_gold.gold_macro_regime` ──► `ai_serving.mv_macro_regime`
```

---

## 8. Open Questions and Risks

### 8.1 Open questions

| # | Question | Owner | Resolution path |
|---|----------|-------|-----------------|
| Q1 | Should `dev_activity_score` use absolute thresholds (e.g. 1000 commits = 100) instead of batch-relative max? | Data | Spike: compute both for one week, compare stability across runs; pick the more useful for Genie. |
| Q2 | DefiLlama `gecko_id` mapping coverage — what fraction of CoinGecko top-200 actually has a DefiLlama entry? | Data | One-shot SQL after first ingest: `SELECT COUNT(*) FROM bronze_defillama_protocols WHERE asset_id IS NOT NULL`. Document in S2 measurement. |
| Q3 | GitHub anonymous rate limit (60/req/h) sufficient for 20 mapped repos × 3 calls = 60? | DataOps | Yes if exactly at limit; safer to require `GITHUB_TOKEN` (5000/h) and treat its absence as a CI-only mode. |
| Q4 | FRED `DXY` (Wall Street Journal) is non-FRED-native — its actual series_id may differ. Likely use `DTWEXBGS` (broad dollar) as primary and add `DXY` as alias if a FRED-published version exists. | Data | Validate live; update job's `FRED_SERIES` constant accordingly. |
| Q5 | Does Genie understand `regime_label` enum strings without a glossary? | AI | Add labels to Genie space description / synonyms when configuring `mv_macro_regime`. |
| Q6 | Should `silver_asset_enriched` be a Type-2 SCD (track historical scores over time) or only carry the latest? | Data | Phase 2 uses latest-only via `ROW_NUMBER`. Type-2 deferred to Phase 3 once retention story is clearer. |

### 8.2 Risks

| ID | Risk | Likelihood | Impact | Mitigation |
|----|------|-----------|--------|-----------|
| R1 | DefiLlama API schema drift (renames `tvl` → `tvlUSD`) | Medium | High (silent NULL fields) | Pin `payload_version`; `validate_enrichment_chain.py` checks for required keys in fixture; alert on row-count drop. |
| R2 | GitHub rate limit 403 in production at scale | Medium | Medium | Gate on `GITHUB_TOKEN` secret being present; make skip-on-403 explicit; Sentinela alert when contributor counts go to NULL across multiple repos in same run. |
| R3 | FRED holiday gaps make `value_30d_ago` stale | High | Low | Use `LAG by date <= obs - 30d` (already in design), not `LAG by row`, so we always pick a real prior observation. |
| R4 | `dev_activity_score` swings wildly run-to-run because batch max changes | Medium | Medium | Either (a) accept and document, (b) switch to absolute thresholds (Q1), or (c) cap normalization denominators with a 30-day rolling max (Phase 3). |
| R5 | Asset–repo map drifts (Polkadot SDK rename, etc.) | Medium | Low | Map is versioned JSON, PR-reviewed; quarterly review checklist in `.agentcodex/ops/`. |
| R6 | `gold_enriched_rankings` join produces row explosion if `silver_asset_enriched` carries duplicates | Low | High | Silver is built with a single-row-per-asset window; explicit unique-on-asset assertion in `validate_enrichment_chain.py` (post-deploy). |
| R7 | Cost regression from 6 h schedules across three new ingestions + a Silver pipeline | Medium | Medium | All jobs use `dependencies: []` (free Databricks runtime), no separate compute. Cost telemetry via existing `ops_usage_ingestion_job`. Re-evaluate after one billing cycle. |
| R8 | Genie answers without provenance for enriched columns | Medium | High | Each Gold view carries `lineage_source`, `freshness_tier`, `freshness_target_minutes`, `quality_status` — same contract as Phase 1 — so Genie response templates can surface them. |
| R9 | Token / API key leaked into Bronze rows via accidental URL logging | Low | High | All HTTP request URLs that include `api_key` (FRED) are constructed inside the job and never written to Spark logs at INFO level; unit test asserts `api_key` is not in any persisted column or stdout. |

### 8.3 Out-of-scope deferrals

- **Streaming / sub-hour freshness** for any enrichment source — deferred until justified by product telemetry.
- **Multi-tenant scoping** of enrichment data — Phase 2 is global; tenant-specific overlays come later.
- **Token cost telemetry for AI consumption of these views** — `ops_usage_ingestion_job` continues to capture this; no Phase 2 changes.
- **DefiLlama historical TVL endpoint (`/tvl/{protocol}`)** — listed in the brief but deferred; current design uses the snapshot in `/protocols`. Add as Phase 2.1 once the protocol-time-series modeling question (Q6) is resolved.

---

## 9. File Manifest and Agent Assignment

| File | Action | Purpose | Suggested agent |
|------|--------|---------|-----------------|
| `databricks/sql/migrations/bronze_enrichment_migration.sql` | Create | Bronze DDL | (general / SQL) |
| `databricks/sql/migrations/silver_enrichment_migration.sql` | Create | Silver DDL | (general / SQL) |
| `databricks/sql/layers/gold_enrichment_views.sql` | Create | Gold views | (general / SQL) |
| `databricks/sql/layers/genie_metric_views.sql` | Edit | Append 3 mv_* views | (general / SQL) |
| `databricks/jobs/bronze_enrichment_table_migration_job.py` | Create | Migration runner | Databricks specialist |
| `databricks/jobs/silver_enrichment_table_migration_job.py` | Create | Migration runner | Databricks specialist |
| `databricks/jobs/defillama_ingestion_job.py` | Create | Bronze ingest | Databricks specialist |
| `databricks/jobs/github_activity_ingestion_job.py` | Create | Bronze ingest | Databricks specialist |
| `databricks/jobs/fred_macro_ingestion_job.py` | Create | Bronze ingest | Databricks specialist |
| `databricks/jobs/silver_enrichment_pipeline_job.py` | Create | Silver materialize | Databricks specialist |
| `databricks/config/github_asset_repo_map.json` | Create | Reference data | (general) |
| `databricks/databricks.yml` | Edit | Bundle resources | DevOps / DAB |
| `databricks/tools/validate_enrichment_chain.py` | Create | Static chain check | (general / Python) |
| `databricks/tools/live_sql_validation.py` | Edit | Add 3 probe queries | (general) |
| `databricks/tests/test_defillama_ingestion_job.py` | Create | Unit tests | Test specialist |
| `databricks/tests/test_github_activity_ingestion_job.py` | Create | Unit tests | Test specialist |
| `databricks/tests/test_fred_macro_ingestion_job.py` | Create | Unit tests | Test specialist |
| `databricks/tests/test_silver_enrichment_pipeline_job.py` | Create | Unit tests | Test specialist |
| `databricks/tests/test_bronze_enrichment_table_migration_job.py` | Create | Unit tests | Test specialist |
| `databricks/tests/test_silver_enrichment_table_migration_job.py` | Create | Unit tests | Test specialist |
| `databricks/tests/test_validate_enrichment_chain.py` | Create | Validator tests | Test specialist |
| `databricks/fixtures/defillama_protocols_sample.json` | Create | Fixture | (general) |
| `databricks/fixtures/github_repo_sample.json` | Create | Fixture | (general) |
| `databricks/fixtures/fred_observations_sample.json` | Create | Fixture | (general) |
| `databricks/unity-catalog-lineage-map.md` | Edit | Append Phase 2 section | (general) |
| `.github/workflows/ci.yml` | Edit | Add tests + deploy steps | DevOps |
| `.agentcodex/ops/approval-gate-policy.md` | Edit | Add 6 new mutation surfaces | (general / docs) |

---

## 10. Pre-flight Checklist (Build Phase Entry)

```text
PRE-FLIGHT CHECK
├─ [x] Existing Phase 1 patterns surveyed and followed
├─ [x] Each Bronze table has single source-of-truth ingestion job
├─ [x] Each Silver table built only from Bronze (no Gold→Silver back-edges)
├─ [x] Each Gold view built only from Silver/Gold (no Bronze→Gold direct, except gold_market_rankings already established)
├─ [x] Each ai_serving view is a thin SELECT * over a Gold view
├─ [x] All schedules use America/Sao_Paulo and quartz cron
├─ [x] All API secrets fetched via dbutils.secrets with env-var fallback
├─ [x] No new pip dependencies introduced (environments.dependencies = [])
├─ [x] Static validator (`validate_enrichment_chain.py`) covers every new object
├─ [x] CI test list updated; deploy step idempotent and approval-gated
├─ [x] Lineage map updated to surface enrichment provenance
└─ [x] Risks enumerated with mitigations
```

---

## Build Sequencing (recommended order for the Build agent)

1. SQL migrations (Bronze + Silver) — no runtime side effects.
2. Migration jobs + their unit tests — exercise SQL load/parse/run.
3. Fixture files for all three sources.
4. Ingestion jobs (DefiLlama, GitHub, FRED) + unit tests in parallel.
5. Silver enrichment pipeline job + unit tests.
6. Gold + ai_serving SQL.
7. Validator (`validate_enrichment_chain.py`) + its test.
8. `databricks.yml` resource additions.
9. CI workflow additions + lineage map + approval-gate policy.
10. Local CI run, then chat-approved `confirm_deploy=true` dispatch.

---

## Status

**DESIGN — Phase 2 Enrichment**: Designed. Ready for `build` phase.
