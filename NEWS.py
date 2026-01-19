import os
import re
import json
import time
import hashlib
import sqlite3
from datetime import timezone
from urllib.parse import quote, urlparse

import requests
import streamlit as st
from dateutil import parser as date_parser
from streamlit_autorefresh import st_autorefresh


# =========================
# CONFIG
# =========================
AUTO_REFRESH_SECONDS = 35
MAX_ARTICLE_AGE_HOURS = 24

RETENTION_DAYS = 30
AI_DIGEST_EVERY_SECONDS = 3600
AI_WINDOW_HOURS_RECENT = 24
AI_CONTEXT_DAYS = 30

DEFAULT_KEYWORDS = ["SPY", "FOMC", "Treasury", "yields", "inflation", "options", "gamma", "liquidity"]

GOOGLE_NEWS_RSS = "https://news.google.com/rss/search?q={q}&hl=en-US&gl=US&ceid=US:en"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"
    )
}

DATABASE_URL = os.getenv("DATABASE_URL", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()


# =========================
# FILTERS
# =========================
INSTITUTIONAL_KEYWORDS = [
    "fomc", "fed", "federal reserve", "powell", "minutes", "dot plot",
    "forward guidance", "terminal rate", "rate path", "restrictive", "accommodative",
    "balance sheet", "runoff", "qt", "qe", "ecb", "boj", "boe",
    "cpi", "ppi", "pce", "core pce", "inflation", "jobs report", "nonfarm payrolls", "nfp",
    "jobless claims", "unemployment", "gdp", "retail sales", "ism", "pmi",
    "treasury", "auction", "bid-to-cover", "bid to cover", "tail",
    "2-year", "2 year", "10-year", "10 year", "real yield", "real yields",
    "yields", "yield curve", "term premium", "curve steepening", "curve flattening",
    "rebalancing", "asset allocation", "positioning", "cta", "risk parity",
    "etf inflows", "etf outflows", "creations", "redemptions",
    "options", "open interest", "gamma", "gamma exposure", "negative gamma", "positive gamma",
    "dealer hedging", "delta hedging", "0dte", "implied volatility", "skew", "vix",
    "liquidity", "funding stress", "financial conditions", "repo", "sofr", "stress",
]

NOISE_KEYWORDS = [
    "meme", "viral", "to the moon", "diamond hands", "paper hands",
    "influencer", "hype", "ape",
    "rockets", "soars", "surges", "plunges",
]

SOURCE_WHITELIST = [
    "reuters.com", "bloomberg.com", "ft.com", "wsj.com",
    "federalreserve.gov", "treasury.gov", "bls.gov", "bea.gov",
    "cnbc.com", "marketwatch.com", "barrons.com",
]

SOURCE_BLACKLIST = [
    "prnewswire.com", "businesswire.com", "globenewswire.com",
    "accesswire.com", "newsfilecorp.com",
    "seekingalpha.com", "themotleyfool.com", "investorplace.com",
]

CLICKBAIT_PHRASES = [
    "what you need to know", "explained", "here's why", "here is why",
    "everything you need to know", "you won't believe",
    "price prediction", "forecast", "top picks", "buy now",
]

MODAL_WEAK_WORDS = [
    "could", "might", "may", "likely", "unlikely",
    "expected", "expected to", "set to", "poised to", "seen as",
]

WIRE_PHRASES = [
    "said in a statement", "in a statement",
    "according to people familiar", "people familiar with the matter",
    "sources said", "data showed", "figures showed",
    "markets repriced", "investors reassessed",
    "traders priced in", "priced in",
]

HIGH_IMPACT_TRIGGERS = [
    "cpi", "core cpi", "ppi", "pce", "core pce",
    "nonfarm payrolls", "nfp", "jobless claims", "unemployment rate",
    "fomc", "fed minutes", "dot plot", "powell",
    "auction", "refunding", "bid-to-cover", "tail",
    "2-year", "10-year", "real yield", "sofr", "repo", "qt",
    "vix", "0dte", "gamma", "dealer hedging", "skew",
]

NEGATIVE_KEYWORDS = [
    "quarterback", "broncos", "giants", "nfl", "nba", "mlb", "nhl", "soccer", "football",
    "rebooking", "flight", "flights", "airline", "visa",
    "brain", "learning", "health", "fitness",
]


# =========================
# UI
# =========================
st.set_page_config(page_title="OZYTARGET — Bloomberg Mode + AI", layout="wide")

st.markdown(
    """
<style>
.stApp { background: linear-gradient(135deg, #0d1117 0%, #161b22 100%); color: #e6edf3; }
.header { color: #79c0ff; font-size: 28px; font-weight: 800; letter-spacing: 1px; font-family: 'Courier New', monospace; }
.card { border-left: 3px solid #1f6feb; padding: 12px 14px; margin-bottom: 10px; background: rgba(20, 20, 30, 0.92); border-radius: 6px; }
.meta { color: #8b949e; font-size: 12px; }
.source { color: #79c0ff; font-size: 12px; font-weight: 700; margin-right: 10px; }
.title { color: #e6edf3; font-size: 15px; font-weight: 650; line-height: 1.35; }
.badge { display:inline-block; padding:2px 8px; border-radius:999px; font-size:11px; margin-left:6px; border:1px solid rgba(121,192,255,.25); color:#79c0ff; }
.small { color:#8b949e; font-size:12px; }
hr { border: 0; border-top: 1px solid rgba(255,255,255,.08); }
</style>
""",
    unsafe_allow_html=True,
)

st_autorefresh(interval=AUTO_REFRESH_SECONDS * 1000, key="auto_refresh_tick")


# =========================
# STATE
# =========================
if "latest_news" not in st.session_state:
    st.session_state["latest_news"] = []
if "last_fetch_ts" not in st.session_state:
    st.session_state["last_fetch_ts"] = 0.0
if "auto_keywords" not in st.session_state:
    st.session_state["auto_keywords"] = DEFAULT_KEYWORDS


# =========================
# HELPERS
# =========================
def safe_parse_time(value: str) -> float:
    if not value:
        return 0.0
    try:
        dt = date_parser.parse(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.timestamp()
    except Exception:
        return 0.0


def time_ago(ts_seconds: float) -> str:
    now = time.time()
    diff = max(0, now - ts_seconds)
    if diff < 60:
        return f"{int(diff)}s"
    if diff < 3600:
        return f"{int(diff // 60)}m"
    return f"{int(diff // 3600)}h"


def count_hits(text: str, keywords: list[str]) -> int:
    s = (text or "").lower()
    hits = 0
    for kw in keywords:
        k = (kw or "").strip().lower()
        if not k:
            continue
        if (" " in k) or ("-" in k):
            if k in s:
                hits += 1
            continue
        if re.search(r"\b" + re.escape(k) + r"\b", s):
            hits += 1
    return hits


def dedupe(items: list[dict]) -> list[dict]:
    seen = set()
    out = []
    for a in items:
        link = (a.get("link") or "").strip()
        if link:
            key = ("link", link)
        else:
            t = re.sub(r"\s+", " ", (a.get("title") or "").strip().lower())
            key = ("title", t[:240])
        if key in seen:
            continue
        seen.add(key)
        out.append(a)
    return out


def _extract_domain(url: str) -> str:
    try:
        host = (urlparse(url).netloc or "").lower()
        return host.replace("www.", "")
    except Exception:
        return ""


def _domain_in(domain: str, patterns: list[str]) -> bool:
    if not domain:
        return False
    return any(p in domain for p in patterns)


def filter_institutional(items: list[dict], min_kw: int, max_noise: int) -> list[dict]:
    out = []
    now_ts = time.time()
    max_age_sec = float(MAX_ARTICLE_AGE_HOURS) * 3600.0

    hard_block_re = re.compile(r"\b(" + "|".join(map(re.escape, NEGATIVE_KEYWORDS)) + r")\b", re.IGNORECASE)

    for a in items:
        title = (a.get("title") or "").strip()
        summary = (a.get("summary") or "").strip()

        if len(title) < 5:
            continue

        ts = float(a.get("_ts") or 0.0)
        if ts <= 0:
            continue

        if (now_ts - ts) > max_age_sec:
            continue

        blob = f"{title}\n{summary}".strip()
        if hard_block_re.search(blob):
            continue

        blob_l = blob.lower()
        kw_hits = count_hits(blob_l, INSTITUTIONAL_KEYWORDS)
        noise_hits = count_hits(blob_l, NOISE_KEYWORDS)

        if kw_hits >= min_kw and noise_hits <= max_noise:
            b = dict(a)
            b["_kw_hits"] = kw_hits
            b["_noise_hits"] = noise_hits
            out.append(b)

    return out


def score_bloomberg(item: dict) -> dict:
    title = (item.get("title") or "").strip()
    summary = (item.get("summary") or "").strip()
    blob = f"{title}\n{summary}".lower()

    domain = _extract_domain(item.get("link") or "")
    score = 0
    reasons = []

    kw_hits = int(item.get("_kw_hits", 0))
    noise_hits = int(item.get("_noise_hits", 0))

    if kw_hits:
        score += min(40, kw_hits * 6)
        reasons.append(f"+inst({kw_hits})")

    hi_hits = count_hits(blob, HIGH_IMPACT_TRIGGERS)
    if hi_hits:
        score += min(30, hi_hits * 8)
        reasons.append(f"+impact({hi_hits})")

    wire_hits = count_hits(blob, WIRE_PHRASES)
    if wire_hits:
        score += min(16, wire_hits * 8)
        reasons.append(f"+wire({wire_hits})")

    if _domain_in(domain, SOURCE_WHITELIST):
        score += 18
        reasons.append("+whitelist")
    if _domain_in(domain, SOURCE_BLACKLIST):
        score -= 28
        reasons.append("-blacklist")

    if noise_hits:
        score -= min(30, noise_hits * 10)
        reasons.append(f"-noise({noise_hits})")

    cb_hits = count_hits(blob, CLICKBAIT_PHRASES)
    if cb_hits:
        score -= min(30, cb_hits * 15)
        reasons.append(f"-clickbait({cb_hits})")

    modal_hits = count_hits(blob, MODAL_WEAK_WORDS)
    if modal_hits:
        score -= min(18, modal_hits * 6)
        reasons.append(f"-modal({modal_hits})")

    score = max(-50, min(100, score))

    out = dict(item)
    out["_domain"] = domain
    out["_score"] = score
    out["_reasons"] = " ".join(reasons[:6])
    return out


def make_item_hash(title: str, link: str) -> str:
    base = (title or "").strip().lower() + "|" + (link or "").strip().lower()
    return hashlib.sha256(base.encode("utf-8")).hexdigest()


# =========================
# DB (Postgres or SQLite)
# =========================
def db_connect():
    if DATABASE_URL:
        try:
            import psycopg2  # psycopg2-binary
            conn = psycopg2.connect(DATABASE_URL)
            return "postgres", conn
        except Exception:
            pass

    conn = sqlite3.connect("news.db", check_same_thread=False)
    return "sqlite", conn


@st.cache_resource
def get_db():
    return db_connect()


def db_init():
    kind, conn = get_db()
    cur = conn.cursor()

    if kind == "postgres":
        cur.execute("""
        CREATE TABLE IF NOT EXISTS news_items (
            id BIGSERIAL PRIMARY KEY,
            item_hash TEXT UNIQUE,
            ts DOUBLE PRECISION,
            source TEXT,
            domain TEXT,
            title TEXT,
            summary TEXT,
            link TEXT,
            score INTEGER,
            kw_hits INTEGER,
            noise_hits INTEGER
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_digests (
            id BIGSERIAL PRIMARY KEY,
            ts DOUBLE PRECISION,
            window_hours INTEGER,
            digest_hour TEXT UNIQUE,
            content_json TEXT
        );
        """)
        # Add digest_hour column if it doesn't exist (migration)
        cur.execute("""
        ALTER TABLE ai_digests ADD COLUMN IF NOT EXISTS digest_hour TEXT;
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS news_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_hash TEXT UNIQUE,
            ts REAL,
            source TEXT,
            domain TEXT,
            title TEXT,
            summary TEXT,
            link TEXT,
            score INTEGER,
            kw_hits INTEGER,
            noise_hits INTEGER
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS ai_digests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts REAL,
            window_hours INTEGER,
            digest_hour TEXT UNIQUE,
            content_json TEXT
        );
        """)
        # SQLite: Add digest_hour column if missing (migration)
        cur.execute("PRAGMA table_info(ai_digests)")
        columns = [col[1] for col in cur.fetchall()]
        if "digest_hour" not in columns:
            cur.execute("ALTER TABLE ai_digests ADD COLUMN digest_hour TEXT;")
    
    conn.commit()


def db_prune_old():
    kind, conn = get_db()
    cutoff_ts = time.time() - (RETENTION_DAYS * 86400.0)
    cur = conn.cursor()
    if kind == "postgres":
        cur.execute("DELETE FROM news_items WHERE ts < %s;", (cutoff_ts,))
    else:
        cur.execute("DELETE FROM news_items WHERE ts < ?;", (cutoff_ts,))
    conn.commit()


def db_upsert_many(items: list[dict]):
    kind, conn = get_db()
    cur = conn.cursor()

    rows = []
    for a in items:
        title = (a.get("title") or "").strip()
        link = (a.get("link") or "").strip()
        item_hash = make_item_hash(title, link)

        rows.append((
            item_hash,
            float(a.get("_ts") or 0.0),
            (a.get("source") or ""),
            (a.get("_domain") or _extract_domain(link)),
            title,
            (a.get("summary") or ""),
            link,
            int(a.get("_score") or 0),
            int(a.get("_kw_hits") or 0),
            int(a.get("_noise_hits") or 0),
        ))

    if not rows:
        return

    if kind == "postgres":
        cur.executemany("""
            INSERT INTO news_items
            (item_hash, ts, source, domain, title, summary, link, score, kw_hits, noise_hits)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (item_hash) DO NOTHING;
        """, rows)
    else:
        cur.executemany("""
            INSERT OR IGNORE INTO news_items
            (item_hash, ts, source, domain, title, summary, link, score, kw_hits, noise_hits)
            VALUES (?,?,?,?,?,?,?,?,?,?);
        """, rows)

    conn.commit()
    db_prune_old()


def db_get_news_since(hours: int, limit: int = 500) -> list[dict]:
    kind, conn = get_db()
    since_ts = time.time() - (hours * 3600.0)
    cur = conn.cursor()

    if kind == "postgres":
        cur.execute("""
            SELECT ts, source, domain, title, summary, link, score, kw_hits, noise_hits
            FROM news_items
            WHERE ts >= %s
            ORDER BY ts DESC
            LIMIT %s;
        """, (since_ts, limit))
    else:
        cur.execute("""
            SELECT ts, source, domain, title, summary, link, score, kw_hits, noise_hits
            FROM news_items
            WHERE ts >= ?
            ORDER BY ts DESC
            LIMIT ?;
        """, (since_ts, limit))

    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({
            "_ts": float(r[0]),
            "source": r[1],
            "_domain": r[2],
            "title": r[3],
            "summary": r[4],
            "link": r[5],
            "_score": int(r[6]),
            "_kw_hits": int(r[7]),
            "_noise_hits": int(r[8]),
        })
    return out


def db_get_latest_digest() -> dict | None:
    kind, conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT ts, content_json FROM ai_digests ORDER BY ts DESC LIMIT 1;")
    row = cur.fetchone()
    if not row:
        return None
    try:
        return {"ts": float(row[0]), "content": json.loads(row[1])}
    except Exception:
        return None


def db_save_digest(content: dict, window_hours: int):
    """
    Idempotent: at most ONE digest per UTC hour.
    Prevents duplicates across Streamlit reruns / Railway multi-instances.
    """
    kind, conn = get_db()
    cur = conn.cursor()

    ts = time.time()
    payload = json.dumps(content, ensure_ascii=False)

    # e.g. "2026-01-18T21" (UTC hour key)
    digest_hour = time.strftime("%Y-%m-%dT%H", time.gmtime(ts))

    if kind == "postgres":
        cur.execute(
            """
            INSERT INTO ai_digests (ts, window_hours, digest_hour, content_json)
            VALUES (%s,%s,%s,%s)
            ON CONFLICT (digest_hour) DO NOTHING;
            """,
            (ts, window_hours, digest_hour, payload),
        )
    else:
        cur.execute(
            """
            INSERT OR IGNORE INTO ai_digests (ts, window_hours, digest_hour, content_json)
            VALUES (?,?,?,?);
            """,
            (ts, window_hours, digest_hour, payload),
        )

    conn.commit()


# =========================
# GEMINI — robust REST (listModels + pick model + JSON-only generateContent)
# =========================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta"


@st.cache_data(ttl=3600, show_spinner=False)
def gemini_list_models() -> list[str]:
    """
    Returns a list of model names available to this API key.
    Cached for 1 hour.
    """
    if not GEMINI_API_KEY:
        return []

    url = f"{GEMINI_BASE}/models"
    headers = {"x-goog-api-key": GEMINI_API_KEY}
    try:
        r = requests.get(url, headers=headers, timeout=20)
        r.raise_for_status()
        data = r.json()
        models = []
        for m in data.get("models", []):
            name = (m.get("name") or "").strip()  # e.g. "models/gemini-2.5-flash"
            if name.startswith("models/"):
                models.append(name.replace("models/", ""))
        return models
    except Exception:
        return []


@st.cache_data(ttl=3600, show_spinner=False)
def gemini_pick_model() -> str | None:
    """
    Picks best available model automatically.
    If listModels fails, falls back to a safe default order (may still 404, but UI won't break).
    """
    models = gemini_list_models()

    preferred = [
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.0-pro",
        "gemini-2.0-flash",
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-pro",
    ]

    # If listModels succeeded
    if models:
        for p in preferred:
            for m in models:
                if m == p or m.startswith(p):
                    return m
        return models[0]

    # If listModels failed, fallback to a reasonable default (best-effort)
    return "gemini-2.5-flash"


def _strip_json_fences(s: str) -> str:
    s2 = (s or "").strip()
    s2 = re.sub(r"^```json\s*", "", s2, flags=re.IGNORECASE)
    s2 = re.sub(r"^```\s*", "", s2)
    s2 = re.sub(r"\s*```$", "", s2)
    return s2.strip()


def gemini_generate_json(prompt: str, debug: bool = False) -> dict:
    """
    Generate JSON from Gemini. Never breaks the UI.
    LOCAL debug: shows raw Gemini output if parsing fails.
    """

    def _default(caption_msg: str, reasoning_msg: str, raw: str = "") -> dict:
        # Always return a full digest shape so UI doesn't show empty base/bull/bear.
        return {
            "caption": caption_msg,
            "reasoning": [
                {"claim": "AI output was not valid JSON", "evidence_ids": [], "why_it_matters": reasoning_msg},
                {"claim": "If you enable Debug AI, you'll see the raw response", "evidence_ids": [], "why_it_matters": ""},
                {"claim": "", "evidence_ids": [], "why_it_matters": ""},
            ],
            "bullets": [],
            "scenarios": {
                "base": {"summary": "", "triggers": [], "evidence_ids": []},
                "bull": {"summary": "", "triggers": [], "evidence_ids": []},
                "bear": {"summary": "", "triggers": [], "evidence_ids": []},
            },
            "watchlist": [],
            "_raw": raw[:2000],
        }

    def _extract_first_json_object(s: str) -> str:
        """
        Extract the first top-level JSON object { ... } from text even if it has
        'Here is...' or other extra text.
        """
        if not s:
            return ""
        s = _strip_json_fences(s)

        start = s.find("{")
        if start < 0:
            return ""

        depth = 0
        in_str = False
        esc = False

        for i in range(start, len(s)):
            ch = s[i]
            if in_str:
                if esc:
                    esc = False
                elif ch == "\\":
                    esc = True
                elif ch == '"':
                    in_str = False
                continue
            else:
                if ch == '"':
                    in_str = True
                    continue
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        return s[start:i + 1]
        return ""

    def _normalize_digest(obj: dict, raw: str = "") -> dict:
        out = dict(obj) if isinstance(obj, dict) else {}
        out.setdefault("caption", "")
        out.setdefault("bullets", [])
        out.setdefault("watchlist", [])
        out.setdefault("scenarios", {})
        out.setdefault("reasoning", [])
        out["_raw"] = raw[:2000]

        # reasoning must be list[dict]
        r = out.get("reasoning")
        if isinstance(r, str):
            out["reasoning"] = [{"claim": r[:260], "evidence_ids": [], "why_it_matters": ""}]
        if not isinstance(out.get("reasoning"), list):
            out["reasoning"] = []

        # pad reasoning to 3
        norm_r = []
        for x in out["reasoning"]:
            if isinstance(x, dict):
                norm_r.append({
                    "claim": str(x.get("claim", "")).strip(),
                    "evidence_ids": x.get("evidence_ids", []) if isinstance(x.get("evidence_ids", []), list) else [],
                    "why_it_matters": str(x.get("why_it_matters", "")).strip(),
                })
            elif isinstance(x, str):
                norm_r.append({"claim": x.strip(), "evidence_ids": [], "why_it_matters": ""})
        while len(norm_r) < 3:
            norm_r.append({"claim": "", "evidence_ids": [], "why_it_matters": ""})
        out["reasoning"] = norm_r[:3]

        # scenarios must exist
        sc = out.get("scenarios")
        if not isinstance(sc, dict):
            sc = {}
        def _norm_one(name: str):
            d = sc.get(name, {})
            if not isinstance(d, dict):
                d = {}
            return {
                "summary": str(d.get("summary", "")).strip(),
                "triggers": d.get("triggers", []) if isinstance(d.get("triggers", []), list) else [],
                "evidence_ids": d.get("evidence_ids", []) if isinstance(d.get("evidence_ids", []), list) else [],
            }
        out["scenarios"] = {"base": _norm_one("base"), "bull": _norm_one("bull"), "bear": _norm_one("bear")}

        if not isinstance(out.get("bullets"), list):
            out["bullets"] = []
        if not isinstance(out.get("watchlist"), list):
            out["watchlist"] = []

        return out

    if not GEMINI_API_KEY:
        return _default("AI disabled (set GEMINI_API_KEY).", "No API key configured.")

    model = gemini_pick_model() or "gemini-2.5-flash"
    url = f"{GEMINI_BASE}/models/{model}:generateContent"
    headers = {"x-goog-api-key": GEMINI_API_KEY}

    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.20,
            "maxOutputTokens": 4500,
            "responseMimeType": "application/json",
        },
    }

    try:
        r = requests.post(url, headers=headers, json=body, timeout=70)
        if r.status_code == 404:
            return _default(f"AI error: model not found ({model})", "Rotate key or check enabled models.")

        r.raise_for_status()
        data = r.json()

        raw_text = ""
        try:
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"] or ""
        except Exception:
            raw_text = ""

        raw_text = raw_text.strip()
        if debug:
            with st.expander("🧪 Gemini RAW (debug)", expanded=True):
                st.write(raw_text if raw_text else "(empty raw text)")
                st.write({"model": model, "has_candidates": bool(data.get("candidates"))})

        if not raw_text:
            return _default("AI returned empty response.", "Empty text from generateContent.")

        # Try parse as JSON directly
        try:
            obj = json.loads(_strip_json_fences(raw_text))
            return _normalize_digest(obj, raw=raw_text)
        except Exception:
            pass

        # Extract first {...} and parse
        extracted = _extract_first_json_object(raw_text)
        if extracted:
            try:
                obj = json.loads(extracted)
                return _normalize_digest(obj, raw=raw_text)
            except Exception:
                return _default("AI parse error.", "Extracted JSON still invalid.", raw=raw_text)

        return _default("AI parse error.", "Could not extract JSON object from Gemini output.", raw=raw_text)

    except Exception as e:
        return _default("AI error.", f"Exception during Gemini call: {type(e).__name__}: {str(e)[:180]}")


def gemini_generate_text(prompt: str, debug: bool = False) -> str:
    """
    Plain text mode (no JSON).
    Fixes: MAX_TOKENS (no parts/text) by:
      - truncating prompt hard
      - increasing maxOutputTokens
      - retrying with a smaller model if needed
    """
    if not GEMINI_API_KEY:
        return "CAPTION:\nAI disabled (set GEMINI_API_KEY)\n\nREASONING:\n- Claim: No API key | Evidence: — | Why: Configure env\n- \n- \n\nSCENARIOS:\nBASE: n/a\nBULL: n/a\nBEAR: n/a\n\nWATCHLIST:\n- Set GEMINI_API_KEY"

    def _fallback(msg: str) -> str:
        return (
            f"CAPTION:\n{msg}\n\nREASONING:\n"
            "- Claim: Model returned no text (likely MAX_TOKENS) | Evidence: — | Why: prompt too large\n"
            "- Claim: Reduce context (24h only) / fewer headlines | Evidence: — | Why: shrink promptTokenCount\n"
            "- Claim: Use flash for speed/short output | Evidence: — | Why: more reliable\n\n"
            "SCENARIOS:\nBASE: n/a\nBULL: n/a\nBEAR: n/a\n\nWATCHLIST:\n"
            "- Reduce prompt size\n- Increase maxOutputTokens\n- Retry"
        )

    def _extract_text(data: dict) -> str:
        # Standard: candidates[0].content.parts[0].text
        try:
            cands = data.get("candidates") or []
            if not cands:
                return ""
            c0 = cands[0] or {}
            content = c0.get("content") or {}
            parts = content.get("parts") or []
            if parts and isinstance(parts[0], dict) and isinstance(parts[0].get("text"), str):
                return parts[0].get("text") or ""
            # Some variants might put text in other places (rare)
            if isinstance(content.get("text"), str):
                return content.get("text") or ""
            if isinstance(c0.get("text"), str):
                return c0.get("text") or ""
            return ""
        except Exception:
            return ""

    def _post(model_name: str, prompt_text: str, max_out: int) -> tuple[str, dict]:
        url = f"{GEMINI_BASE}/models/{model_name}:generateContent"
        headers = {"x-goog-api-key": GEMINI_API_KEY, "Content-Type": "application/json"}
        body = {
            "contents": [{"parts": [{"text": prompt_text}]}],
            "generationConfig": {
                "temperature": 0.25,
                "maxOutputTokens": int(max_out),
            },
        }
        r = requests.post(url, headers=headers, json=body, timeout=70)
        data = {}
        try:
            data = r.json()
        except Exception:
            data = {"_raw": r.text[:2000], "_status": r.status_code}

        if debug:
            with st.expander("🧪 Full Gemini Response (debug)", expanded=True):
                st.json(data)
                st.write({"model": model_name, "status": r.status_code})

        # Handle HTTP errors
        if r.status_code == 404:
            return "", {"error": "404", "data": data}
        if r.status_code >= 400:
            return "", {"error": f"http_{r.status_code}", "data": data}

        txt = _extract_text(data).strip()
        return txt, data

    # ---- HARD TRUNCATION: keep prompt small & safe ----
    # Keep last chunk (usually includes headline packs) and cap size in chars.
    # This prevents promptTokenCount exploding.
    prompt = (prompt or "").strip()
    MAX_CHARS = 10000  # reduced from 18000; prevents MAX_TOKENS error
    if len(prompt) > MAX_CHARS:
        prompt = prompt[-MAX_CHARS:]

    # Primary model: pick, but avoid pro for manual if prompt is large
    primary = gemini_pick_model() or "gemini-2.5-flash"

    # Try 1: primary, bigger output
    txt, data = _post(primary, prompt, max_out=3500)
    if txt:
        return txt

    # If finishReason says MAX_TOKENS or no parts/text, retry with smaller prompt + flash
    finish = ""
    try:
        finish = ((data.get("candidates") or [{}])[0].get("finishReason") or "")
    except Exception:
        finish = ""

    # Shrink prompt harder and retry
    prompt2 = prompt[-9000:] if len(prompt) > 9000 else prompt

    # Try 2: force flash (more reliable + faster)
    txt2, data2 = _post("gemini-2.5-flash", prompt2, max_out=3500)
    if txt2:
        return txt2

    # Try 3: flash with even smaller prompt
    prompt3 = prompt2[-5000:] if len(prompt2) > 5000 else prompt2
    txt3, data3 = _post("gemini-2.5-flash", prompt3, max_out=3000)
    if txt3:
        return txt3

    # Final fallback message (include finish reason to teach what happened)
    reason = finish or "NO_TEXT"
    return _fallback(f"AI produced no text (finishReason={reason}). Prompt too large / MAX_TOKENS.")


def _pack(items: list[dict], n: int) -> str:
    lines = []
    for a in items[:n]:
        lines.append(f"- [{a.get('_domain','')}] {a.get('title','')} (score={a.get('_score',0)}) | {a.get('link','')}")
    return "\n".join(lines)


def build_digest_prompt(recent_24h: list[dict], context_30d: list[dict]) -> str:
    def _pack_with_ids(items: list[dict], n: int) -> str:
        lines = []
        for i, a in enumerate(items[:n], start=1):
            dom = a.get("_domain", "")
            title = (a.get("title", "") or "").strip().replace("\n", " ")
            score = a.get("_score", 0)
            link = a.get("link", "")
            lines.append(f"[H{i}] ({dom}) score={score} | {title} | {link}")
        return "\n".join(lines)

    recent_txt = _pack_with_ids(recent_24h, 20)
    context_txt = _pack_with_ids(context_30d, 20)

    return f"""
You are a Bloomberg-style markets editor. Output ONLY valid JSON (no markdown).

JSON SCHEMA:
{{
  "caption": "<2 lines max>",
  "reasoning": [
    {{"claim": "...", "evidence_ids": ["H1"], "why": "..."}},
    {{"claim": "...", "evidence_ids": ["H2"], "why": "..."}}
  ],
  "scenarios": {{
    "bull": "...",
    "bear": "..."
  }},
  "watchlist": ["item1", "item2"]
}}

RULES:
- Do NOT invent facts.
- Use only headlines H1-H20.
- Output ONLY valid JSON, nothing else.

24H HEADLINES:
{recent_txt}

30D CONTEXT:
{context_txt}
""".strip()


def build_manual_ai_prompt_from_latest(latest_items: list[dict]) -> str:
    def pack(items: list[dict], n: int = 12) -> str:
        lines = []
        for i, a in enumerate(items[:n], start=1):
            dom = a.get("_domain", "")
            title = (a.get("title", "") or "").strip().replace("\n", " ")
            score = a.get("_score", 0)
            # NO metas link entero (consume tokens). Solo dominio+título.
            lines.append(f"[N{i}] ({dom}) score={score} | {title}")
        return "\n".join(lines)

    return f"""
You are a Bloomberg-style markets editor.

Return ONLY plain text. No JSON. No markdown.

CAPTION:
<1-2 lines>

REASONING (3 bullets, cite N#):
- Claim: ... | Evidence: N#,N# | Why: ...
- Claim: ... | Evidence: N# | Why: ...
- Claim: ... | Evidence: N#,N# | Why: ...

SCENARIOS:
BASE: <2-4 lines: 2y/10y, USD, sectors> | Evidence: N#,N#
BULL: <2-4 lines> | Evidence: N#
BEAR: <2-4 lines> | Evidence: N#,N#

WATCHLIST (next 24h; 6 items):
- ...
- ...
- ...
- ...
- ...
- ...

═══════════════════════════════════════════════════════════════

📈 BULLISH ASSETS (1-7 DAYS):
- Asset: <ticker> | Target: <level> | Why: <reason> | Conf: HIGH/MED
- Asset: <ticker> | Target: <level> | Why: <reason> | Conf: HIGH/MED

📉 BEARISH ASSETS (1-7 DAYS):
- Asset: <ticker> | Stop: <level> | Why: <risk> | Conf: HIGH/MED
- Asset: <ticker> | Stop: <level> | Why: <risk> | Conf: HIGH/MED

═══════════════════════════════════════════════════════════════

HEADLINES:
{pack(latest_items, 12)}
""".strip()


def run_manual_ai_analysis(latest_items: list[dict], debug: bool = False) -> str:
    if not latest_items:
        return "CAPTION:\nINSUFFICIENT DATA\n\nREASONING:\n- Claim: No headlines loaded yet | Evidence: — | Why: Press Refresh NOW first\n- Claim:  | Evidence: — | Why: \n- Claim:  | Evidence: — | Why: \n\nSCENARIOS:\nBASE:  | Evidence: —\nBULL:  | Evidence: —\nBEAR:  | Evidence: —\n\nTRIGGERS:\n- \n- \n- \n- \n- \n- \n\nWATCHLIST:\n- \n- \n- \n- \n- \n- "

    prompt = build_manual_ai_prompt_from_latest(latest_items)
    return gemini_generate_text(prompt, debug=debug)


def maybe_generate_ai_digest() -> dict | None:
    """
    Stores digest as TEXT inside ai_digests.content_json (string).
    This avoids JSON parsing instability entirely.
    """
    latest = db_get_latest_digest()
    now_ts = time.time()
    if latest and (now_ts - latest["ts"]) < AI_DIGEST_EVERY_SECONDS:
        c = latest["content"]
        if isinstance(c, dict):
            return c
        return {"caption": str(c)}

    recent_24h = db_get_news_since(hours=AI_WINDOW_HOURS_RECENT, limit=600)
    context_30d = db_get_news_since(hours=AI_CONTEXT_DAYS * 24, limit=1000)
    context_30d.sort(key=lambda x: (x.get("_score", 0), x.get("_ts", 0.0)), reverse=True)

    prompt = build_digest_prompt(recent_24h, context_30d)
    debug = st.session_state.get("debug_ai", False)
    content = gemini_generate_json(prompt, debug=debug)
    db_save_digest(content, window_hours=AI_WINDOW_HOURS_RECENT)
    return content


# =========================
# FETCHERS
# =========================
def fetch_google_news(keywords: list[str]) -> list[dict]:
    base = " OR ".join(keywords) if keywords else "SPY"
    when = "when:1d" if MAX_ARTICLE_AGE_HOURS <= 24 else "when:2d"
    negative = " ".join([f"-{w}" for w in NEGATIVE_KEYWORDS])
    query = f"({base}) {when} {negative}"

    feed = requests.get(GOOGLE_NEWS_RSS.format(q=quote(query)), headers=HEADERS, timeout=12)
    feed.raise_for_status()

    import feedparser
    parsed = feedparser.parse(feed.content)

    items = []
    for e in parsed.entries[:60]:
        title = getattr(e, "title", "") or ""
        link = getattr(e, "link", "") or ""
        published = getattr(e, "published", "") or ""
        summary = getattr(e, "summary", "") or ""
        ts = safe_parse_time(published)

        items.append({
            "source": "OZYTARGET.COM",
            "title": title.strip(),
            "link": link.strip(),
            "time": published.strip(),
            "summary": summary.strip(),
            "_ts": ts,
        })
    return items


# =========================
# PIPELINE (cached)
# =========================
feed_box = st.container()

@st.cache_data(ttl=AUTO_REFRESH_SECONDS, show_spinner=False)
def fetch_all_sources_cached(keywords: list[str], min_kw: int, max_noise: int, cache_buster: int = 0) -> list[dict]:
    # IMPORTANT:
    # "cache_buster" MUST be used inside the function so Streamlit cache key changes.
    _ = int(cache_buster)

    items: list[dict] = []

    try:
        items.extend(fetch_google_news(keywords))
    except Exception:
        pass

    items = dedupe(items)
    items = filter_institutional(items, min_kw=min_kw, max_noise=max_noise)
    items = [score_bloomberg(x) for x in items]

    # Most recent first (you requested recency first)
    items.sort(key=lambda x: x.get("_ts", 0.0), reverse=True)
    return items


# =========================
# INIT DB
# =========================
db_init()


# =========================
# SETTINGS + REFRESH
# =========================
st.markdown("---")
combined_input = st.text_input(
    "Enter keywords (comma-separated)",
    value=", ".join(st.session_state["auto_keywords"]),
    key="combined_keywords_input"
)
manual_keywords = [k.strip() for k in combined_input.split(",") if k.strip()]
st.session_state["auto_keywords"] = manual_keywords

# ⚡ Filter Settings (hidden, using defaults)
min_kw_hits = 1  # Default: Min KW = 1
max_noise_hits = 0  # Default: Noise = 0

colA, colB, colC2 = st.columns([1, 1, 2])
with colA:
    force_refresh = st.button("🔄 Refresh Data", use_container_width=True, key="force_refresh_now")
with colB:
    flush_cache = st.button("🧹 Clear Cache", use_container_width=True, key="flush_cache_now")
with colC2:
    st.markdown(
        f"<div class='small'>Auto-refresh {AUTO_REFRESH_SECONDS}s | Cutoff {MAX_ARTICLE_AGE_HOURS}h | Retention {RETENTION_DAYS}d | AI hourly</div>",
        unsafe_allow_html=True
    )

if flush_cache:
    st.cache_data.clear()
    st.session_state["last_fetch_ts"] = 0.0
    st.success("✅ Cache flushed")


# =========================
# DEBUG (LOCAL)
# =========================
debug_ai = False  # Show only processed output (cooked)


# =========================
# AI MANUAL TRIGGER (recommended)
# =========================
st.markdown("#### 📊 Headline Analysis")
col_ai1, col_ai2 = st.columns([1, 3])

with col_ai1:
    run_ai_now = st.button("📊 Analyze Headlines", use_container_width=True, key="run_ai_now_btn")

with col_ai2:
    st.caption("Ejecuta el razonamiento SOLO cuando tú lo pidas (más estable que auto-hourly).")

if "ai_manual_result" not in st.session_state:
    st.session_state["ai_manual_result"] = None
if "ai_manual_ts" not in st.session_state:
    st.session_state["ai_manual_ts"] = 0.0

if "custom_ai_input" not in st.session_state:
    st.session_state["custom_ai_input"] = ""
if "custom_ai_result" not in st.session_state:
    st.session_state["custom_ai_result"] = None


# =========================
# CUSTOM AI REASONING (Manual input)
# =========================
st.markdown("#### 📰 Custom News Analysis")
st.caption("Paste market news, data, or headlines for AI-powered analysis.")

custom_input = st.text_area(
    "Enter data/news/headlines:",
    value=st.session_state.get("custom_ai_input", ""),
    height=120,
    key="custom_input_area",
    placeholder="Paste market news, headlines, or any data here..."
)

col_custom1, col_custom2 = st.columns([1, 3])
with col_custom1:
    run_custom_ai = st.button("� Analyze Custom Data", use_container_width=True, key="run_custom_ai_btn")

with col_custom2:
    st.caption("AI will analyze and provide reasoning on your custom input.")

if run_custom_ai and custom_input.strip():
    st.session_state["custom_ai_input"] = custom_input
    custom_prompt = f"""
You are a Bloomberg-style markets analyst.

Return ONLY plain text. No JSON. No markdown.

CAPTION:
<1-2 lines terminal-style summary>

REASONING (3 bullets):
- Claim: ... | Evidence: From input | Why: ...
- Claim: ... | Evidence: From input | Why: ...
- Claim: ... | Evidence: From input | Why: ...

═══════════════════════════════════════════════════════════════

📈 BULLISH RECOMMENDATIONS (1-7 DAYS):
- Asset 1 | Ticker: <SPY/QQQ/etc> | Why: <reason from input>
- Asset 2 | Ticker: <sector/ticker> | Why: <reason from input>
- Asset 3 | Ticker: <sector/ticker> | Why: <reason from input>

═══════════════════════════════════════════════════════════════

📉 BEARISH / SHORT CANDIDATES (1-7 DAYS):
- Asset 1 | Ticker: <sector/ticker> | Why: <risk from input>
- Asset 2 | Ticker: <sector/ticker> | Why: <risk from input>
- Asset 3 | Ticker: <sector/ticker> | Why: <risk from input>

═══════════════════════════════════════════════════════════════

INPUT DATA:
{custom_input}
""".strip()
    
    with st.spinner("⚡ ANALYZER BY OZYTARGET.COM..."):
        try:
            custom_result = gemini_generate_text(custom_prompt, debug=True)
            st.session_state["custom_ai_result"] = custom_result
        except Exception as e:
            st.session_state["custom_ai_result"] = f"CAPTION:\nAI ERROR\n\nREASONING:\n- Claim: Exception | Evidence: — | Why: {type(e).__name__}: {str(e)[:180]}"

if st.session_state.get("custom_ai_result"):
    st.markdown("---")
    st.markdown("### 🤖 pro-analizer")
    st.text(st.session_state["custom_ai_result"])


# =========================
# AUTO FETCH + STORE
# =========================
now_ts = time.time()
should_fetch = force_refresh or ((now_ts - st.session_state.get("last_fetch_ts", 0.0)) >= AUTO_REFRESH_SECONDS)

if should_fetch:
    with st.spinner("Auto-fetching latest news..."):
        buster = int(now_ts) if force_refresh else 0
        fresh = fetch_all_sources_cached(
            keywords=manual_keywords if manual_keywords else DEFAULT_KEYWORDS,
            min_kw=min_kw_hits,
            max_noise=max_noise_hits,
            cache_buster=buster,
        )
        st.session_state["latest_news"] = fresh
        st.session_state["last_fetch_ts"] = now_ts

        try:
            db_upsert_many(fresh)
        except Exception as e:
            st.warning(f"DB write error: {e}")


# =========================
# RUN AI (MANUAL) — at the end of the tape, on demand
# =========================
if run_ai_now:
    latest_now = st.session_state.get("latest_news") or []
    with st.spinner("📊 Analyzing headlines..."):
        try:
            txt = run_manual_ai_analysis(latest_now, debug=True)  # Always debug for manual button
            st.session_state["ai_manual_result"] = txt
            st.session_state["ai_manual_ts"] = time.time()
        except Exception as e:
            st.session_state["ai_manual_result"] = f"CAPTION:\nAI ERROR\n\nREASONING:\n- Claim: Exception | Evidence: — | Why: {type(e).__name__}: {str(e)[:180]}"
            st.session_state["ai_manual_ts"] = time.time()


# =========================
# AI DIGEST (Hourly) — run AFTER fetch + DB upsert
# =========================
# Gate: only try AI if we have enough fresh headlines saved (prevents "reasoning on nothing")
min_items_for_ai = 8

# Picked model (for AI operations, not displayed)
picked_model = gemini_pick_model()

ai_digest = None
try:
    # Ensure we reason on the newest state:
    # - latest_news updated this run (if should_fetch)
    # - db_upsert_many already executed right above when should_fetch is True
    latest_now = st.session_state.get("latest_news") or []
    if len(latest_now) >= min_items_for_ai:
        ai_digest = maybe_generate_ai_digest()
    else:
        ai_digest = {
            "caption": "AI waiting for more headlines...",
            "reasoning": [
                {"claim": "Not enough fresh headlines yet for a solid digest.", "evidence_ids": [], "why_it_matters": f"Need ≥ {min_items_for_ai} items."},
                {"claim": "", "evidence_ids": [], "why_it_matters": ""},
                {"claim": "", "evidence_ids": [], "why_it_matters": ""},
            ],
            "bullets": [],
            "scenarios": {
                "base": {"summary": "", "triggers": [], "evidence_ids": []},
                "bull": {"summary": "", "triggers": [], "evidence_ids": []},
                "bear": {"summary": "", "triggers": [], "evidence_ids": []},
            },
            "watchlist": [],
        }
except Exception as e:
    ai_digest = {
        "caption": f"AI digest error: {e}",
        "reasoning": [
            {"claim": "AI failed to generate digest.", "evidence_ids": [], "why_it_matters": str(e)[:180]},
            {"claim": "", "evidence_ids": [], "why_it_matters": ""},
            {"claim": "", "evidence_ids": [], "why_it_matters": ""},
        ],
        "bullets": [],
        "scenarios": {
            "base": {"summary": "", "triggers": [], "evidence_ids": []},
            "bull": {"summary": "", "triggers": [], "evidence_ids": []},
            "bear": {"summary": "", "triggers": [], "evidence_ids": []},
        },
        "watchlist": [],
    }


# =========================
# RENDER
# =========================
with feed_box:
    st.markdown('<div class="header">OZYTARGET NEWS</div>', unsafe_allow_html=True)
    st.markdown("---")

    news = st.session_state.get("latest_news") or []
    if not news:
        st.info("📰 Loading news... (first fetch usually takes a few seconds)")
    else:
        for a in news[:80]:
            st.markdown(
                f"""
<div class="card">
  <div class="meta">
    <span class="source">{a.get('source','')}</span>
    <span>{time_ago(a.get('_ts', 0.0))} ago</span>
    <span class="badge">score={a.get('_score', 0)}</span>
    <span class="badge">kw={a.get('_kw_hits', 0)}</span>
    <span class="badge">noise={a.get('_noise_hits', 0)}</span>
    <span class="badge">{a.get('_domain','')}</span>
    <span style="margin-left:10px;">| {a.get('time','')}</span>
  </div>
  <div class="title">
    <a href="{a.get('link','')}" target="_blank" style="color:#e6edf3; text-decoration:none;">
      {a.get('title','')}
    </a>
    <span class="badge" style="margin-left:8px;">{a.get('_reasons','')}</span>
  </div>
</div>
""",
                unsafe_allow_html=True,
            )

# =========================
# AI OUTPUT (MANUAL) — at the very end of the news list
# =========================
ai_txt = st.session_state.get("ai_manual_result")
if ai_txt:
    st.markdown("---")
    st.markdown("## 🤖 pro-analizer")
    st.caption(f"Generated: {time_ago(st.session_state.get('ai_manual_ts', 0.0))} ago")
    st.markdown(f"""
    <div style="max-height: 800px; overflow-y: auto; border: 1px solid #1f6feb; padding: 12px; border-radius: 6px; background: rgba(20, 20, 30, 0.92);">
    <pre style="white-space: pre-wrap; word-wrap: break-word; color: #e6edf3; font-family: 'Courier New', monospace; font-size: 12px; margin: 0;">{ai_txt}</pre>
    </div>
    """, unsafe_allow_html=True)

# =========================
# FOOTER
# =========================
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; font-size: 12px; color: #8b949e; margin-top: 20px;">
    Developed by ozy | © 2026 | Mode News Scanner | 
    <a href="https://ozytarget.com" target="_blank" style="color: #79c0ff; text-decoration: none;">ozytarget.com</a> | 
    <a href="https://protdr.com" target="_blank" style="color: #79c0ff; text-decoration: none;">protdr.com</a>
    </div>
    """,
    unsafe_allow_html=True
)