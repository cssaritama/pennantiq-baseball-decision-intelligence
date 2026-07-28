from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from src.pennantiq.agent import generate_answer
from src.pennantiq.analytics import adaptation_signals, add_features, build_brief
from src.pennantiq.backtest import run_shadow_mode
from src.pennantiq.council import run_decision_council
from src.pennantiq.context import (
    available_dimensions,
    context_matrix,
    context_split_table,
    enrich_context,
)
from src.pennantiq.data import (
    dataset_profile,
    load_pitches,
    load_recent_results,
    load_uploaded_csv,
)
from src.pennantiq.data_catalog import catalog_health, source_table
from src.pennantiq.decision_memory import decision_metrics, decisions, log_decision
from src.pennantiq.monitoring import interactions, log_interaction, record_feedback
from src.pennantiq.organization import organization_profiles
from src.pennantiq.starter_readiness import debutant_protocol, starter_assessment

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parent

st.set_page_config(
    page_title="PennantIQ — Baseball Data Intelligence",
    page_icon="⚾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
:root{--gold:#d2b06f;--ivory:#f5f1e8;--muted:#aeb9ca;--navy:#06101f;--panel:#0b1728;--line:#253a58;--good:#55c99a;--risk:#e98181}
.stApp{background:radial-gradient(circle at 12% -10%,#1b335f 0,#091426 31%,#03070d 72%);color:var(--ivory)}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#07101d,#03070c);border-right:1px solid #182a43}
[data-testid="stMetric"]{background:linear-gradient(145deg,rgba(17,31,53,.92),rgba(7,14,25,.94));border:1px solid var(--line);padding:1rem;border-radius:18px}
.hero{padding:2.25rem 2.4rem;border:1px solid #2b4365;border-radius:24px;background:linear-gradient(135deg,rgba(23,43,77,.96),rgba(5,11,21,.96));box-shadow:0 28px 90px rgba(0,0,0,.36);margin-bottom:1rem}
.eyebrow{letter-spacing:.23em;color:var(--gold);font-weight:800;font-size:.75rem}.hero h1{font-size:3.25rem;margin:.35rem 0 .25rem;line-height:1}.hero p{max-width:940px}.muted{color:var(--muted)}
.signal{padding:1rem 1.1rem;border:1px solid #293c58;border-radius:16px;background:rgba(8,17,31,.82);height:100%}.signal h4{margin:0 0 .3rem;color:var(--gold)}
.badge{display:inline-block;padding:.25rem .6rem;border-radius:999px;background:#152944;border:1px solid #34567f;color:#e0ecff;font-size:.76rem;font-weight:700;letter-spacing:.04em}
.promise{border-left:3px solid var(--gold);padding:.7rem 1rem;background:rgba(210,176,111,.07);border-radius:0 12px 12px 0}
.small{font-size:.86rem}.stButton>button{border-radius:12px;font-weight:700}.stTabs [data-baseweb="tab-list"]{gap:.4rem}.stTabs [data-baseweb="tab"]{border-radius:12px;background:#0b1829;border:1px solid #203653;padding:.55rem .85rem}
hr{border-color:#1f314b}.block-container{padding-top:1.5rem;max-width:1500px}
</style>
""",
    unsafe_allow_html=True,
)


@st.cache_data
def _load_default():
    return load_pitches()


@st.cache_data(show_spinner=False)
def _shadow(dataframe: pd.DataFrame):
    return run_shadow_mode(dataframe)


@st.cache_data(show_spinner=False)
def _enriched(dataframe: pd.DataFrame):
    return enrich_context(dataframe)


@st.cache_data(show_spinner=False)
def _recent_results():
    return load_recent_results()


def _hero():
    st.markdown(
        """
<div class="hero">
  <div class="eyebrow">BASEBALL DECISION INTELLIGENCE · MULTI-AGENT COUNCIL · GCP-READY</div>
  <h1>PennantIQ</h1>
  <p style="font-size:1.28rem"><b>Championships are won in moments. Dynasties are built in systems.</b></p>
  <p class="muted">Unify pitch data, context, evidence and human judgment. Prepare before the game, record the choice, replay it after the game and turn every series into organizational knowledge.</p>
  <span class="badge">PUBLIC OPEN-CORE PROTOTYPE · v0.1.0</span>
</div>
""",
        unsafe_allow_html=True,
    )


def _evidence_color(label: str) -> str:
    return {"strong": "🟢", "moderate": "🟡", "weak": "🟠", "insufficient": "🔴"}.get(label, "⚪")


# Sidebar: deterministic bundled data by default, optional user-owned Statcast upload.
st.sidebar.markdown("## PennantIQ")
st.sidebar.caption("Baseball Decision Intelligence Platform")
profiles = organization_profiles()
org_labels = {v["display_name"]: k for k, v in profiles.items()}
org_label = st.sidebar.selectbox("Organization context", list(org_labels), index=0) if org_labels else "Demo Professional Club"
organization = profiles.get(org_labels.get(org_label, ""), {"display_name": org_label, "objective": "decision quality"})
st.sidebar.caption(f"Objective: {organization.get('objective', 'decision quality')}")
uploaded = st.sidebar.file_uploader(
    "Use your own Statcast-compatible CSV",
    type=["csv"],
    help="The file is processed in memory. PennantIQ normalizes common Baseball Savant/pybaseball fields.",
)
try:
    if uploaded is not None:
        df = load_uploaded_csv(uploaded)
        active_mode = "uploaded real data"
    else:
        df = _load_default()
        active_mode = "bundled reproducible demo"
except Exception as exc:
    st.error(f"The selected dataset could not be loaded: {exc}")
    st.stop()

profile = dataset_profile(df)
x = _enriched(df)
real_results = _recent_results()

st.sidebar.markdown(f"**Mode:** `{active_mode}`")
st.sidebar.caption(f"{profile['rows']:,} pitches · {profile['games']} games")
st.sidebar.caption("Real New York results snapshot is shown separately in Command Center.")
page = st.sidebar.radio(
    "Workspace",
    [
        "Command Center",
        "Starter Pulse",
        "Matchup Lab",
        "Decision Council",
        "Context Matrix",
        "Shadow Mode",
        "Ask PennantIQ",
        "Decision Ritual",
        "Trust & Monitoring",
        "GCP Platform",
        "Roadmap",
    ],
)
st.sidebar.markdown("---")
st.sidebar.caption(
    "Independent research prototype. Not affiliated with or endorsed by MLB or any MLB club. "
    "No championship, medical or causal guarantee is made."
)

_hero()

if page == "Command Center":
    st.markdown("## Command Center")
    st.caption("A single view of data freshness, team trajectory, evidence coverage and platform readiness.")
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Pitch records", f"{profile['rows']:,}")
    c2.metric("Games", profile["games"])
    c3.metric("Pitchers", profile["pitchers"])
    c4.metric("Context gaps", len(profile["missing_context"]))
    health = catalog_health()
    c5.metric("Registered sources", health["registered_sources"])

    st.markdown(
        """<div class="promise"><b>Mission:</b> help a championship organization increase the quality, speed and accountability of its decisions. The mission can aim at returning New York to October glory; the product must never sell an unverifiable title guarantee.</div>""",
        unsafe_allow_html=True,
    )

    st.markdown("### Real New York pulse — frozen factual snapshot")
    if real_results.empty:
        st.info("No real results snapshot is bundled.")
    else:
        teams = sorted(real_results["team"].unique())
        selected_team = st.segmented_control("Team", teams, default=teams[0])
        team_results = real_results[real_results["team"] == selected_team].copy()
        team_results["run_diff"] = team_results["team_score"] - team_results["opponent_score"]
        wins = int((team_results["result"] == "W").sum())
        losses = int((team_results["result"] == "L").sum())
        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Snapshot record", f"{wins}-{losses}")
        r2.metric("Run differential", f"{team_results['run_diff'].sum():+d}")
        r3.metric("Home record", f"{int(((team_results.home_away=='home')&(team_results.result=='W')).sum())}-{int(((team_results.home_away=='home')&(team_results.result=='L')).sum())}")
        r4.metric("Away record", f"{int(((team_results.home_away=='away')&(team_results.result=='W')).sum())}-{int(((team_results.home_away=='away')&(team_results.result=='L')).sum())}")
        chart = team_results.sort_values("game_date")
        st.plotly_chart(
            px.bar(
                chart,
                x="game_date",
                y="run_diff",
                hover_data=["opponent", "team_score", "opponent_score", "home_away"],
                title="Game-level run differential — included real snapshot",
            ),
            use_container_width=True,
        )
        st.caption("This bundled snapshot contains final scores only. It is not used as pitch-level evidence.")

    st.markdown("### Data portfolio")
    catalog = source_table()
    if not catalog.empty:
        st.dataframe(
            catalog[["name", "mode", "grain", "coverage", "status", "license", "included"]],
            use_container_width=True,
            hide_index=True,
        )

    st.markdown("### Current pitch-data profile")
    st.json(profile)

elif page == "Starter Pulse":
    st.markdown("## Starter Pulse")
    st.caption("Describe how a pitcher is arriving—without turning form signals into medical or causal claims.")
    pitcher = st.selectbox("Pitcher", sorted(df.pitcher_name.dropna().unique()), key="starter_pitcher")
    last_n = st.slider("Recent appearances", 2, 10, 5)
    assessment, starts = starter_assessment(df, pitcher, last_n=last_n)
    a = assessment.to_dict()
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Form Index", "—" if a["form_index"] is None else f"{a['form_index']:.1f}")
    c2.metric("Evidence", f"{_evidence_color(a['evidence'])} {a['evidence'].title()}")
    c3.metric("Velocity Δ", "—" if a["velocity_delta"] is None else f"{a['velocity_delta']:+.2f} mph")
    c4.metric("Whiff Δ", "—" if a["whiff_delta"] is None else f"{a['whiff_delta']:+.1%}")
    c5.metric("Hard-contact Δ", "—" if a["hard_contact_delta"] is None else f"{a['hard_contact_delta']:+.1%}")
    st.info(a["summary"])

    if not starts.empty:
        left, right = st.columns(2)
        with left:
            st.plotly_chart(
                px.line(starts, x="game_date", y="avg_velocity", markers=True, title="Velocity by appearance"),
                use_container_width=True,
            )
        with right:
            st.plotly_chart(
                px.line(
                    starts,
                    x="game_date",
                    y=["whiff_rate", "hard_contact_rate"],
                    markers=True,
                    title="Whiff and hard-contact signals",
                ),
                use_container_width=True,
            )
        st.dataframe(starts.tail(last_n).sort_values("game_date", ascending=False), use_container_width=True, hide_index=True)

    with st.expander("Debutant and sparse-history protocol", expanded=a["mode"] != "observed_form"):
        st.json(debutant_protocol(df, pitcher))
    for limitation in a["limitations"]:
        st.warning(limitation)

elif page == "Matchup Lab":
    st.markdown("## Matchup Lab")
    st.caption("Pitcher–batter scenario support with evidence strength, alternatives and abstention.")
    c1, c2 = st.columns(2)
    pitcher = c1.selectbox("Pitcher", sorted(df.pitcher_name.unique()), key="match_pitcher")
    batter = c2.selectbox("Batter", sorted(df.batter_name.unique()), key="match_batter")
    c3, c4 = st.columns(2)
    balls = c3.selectbox("Balls", [0, 1, 2, 3])
    strikes = c4.selectbox("Strikes", [0, 1, 2], index=2)
    brief = build_brief(df, pitcher, batter, balls, strikes)
    if brief["abstain"]:
        st.error("Insufficient evidence for a reliable player-specific recommendation. Human review is required.")

    cols = st.columns(3)
    for col, label, key in zip(cols, ["Plan A", "Plan B", "Avoid"], ["plan_a", "plan_b", "avoid"]):
        value = brief[key]
        with col:
            st.markdown(f"<div class='signal'><h4>{label}</h4>", unsafe_allow_html=True)
            if value:
                st.markdown(f"**{value['pitch_family'].title()} · {value['zone_group'].title()}**")
                st.caption(
                    f"n={value['n']} · {_evidence_color(value['confidence'])} {value['confidence']} evidence · posterior value {value['posterior_value']:.3f}"
                )
            else:
                st.write("No supported candidate")
            st.markdown("</div>", unsafe_allow_html=True)

    signals = adaptation_signals(df, batter)
    if not signals.empty:
        st.plotly_chart(
            px.bar(
                signals,
                x="pitch_family",
                y="value_shift",
                hover_data=["early_n", "recent_n", "early_whiff", "recent_whiff"],
                title="Opponent Adaptation Signals — recent minus earlier window",
            ),
            use_container_width=True,
        )
    st.caption(brief["method"])

elif page == "Decision Council":
    st.markdown("## PennantIQ Decision Council")
    st.caption("Specialized evidence agents challenge the same decision before a Chief Strategy layer synthesizes the brief. The public release is deterministic and auditable; Team mode is designed for Vertex AI ADK.")
    c1, c2 = st.columns(2)
    pitcher = c1.selectbox("Pitcher", sorted(df.pitcher_name.unique()), key="council_pitcher")
    batter = c2.selectbox("Batter", sorted(df.batter_name.unique()), key="council_batter")
    c3, c4 = st.columns(2)
    balls = c3.selectbox("Balls", [0, 1, 2, 3], key="council_balls")
    strikes = c4.selectbox("Strikes", [0, 1, 2], index=2, key="council_strikes")
    council = run_decision_council(df, pitcher, batter, balls, strikes, organization)
    st.markdown(f"**Organization lens:** {organization.get('display_name')}  ")
    st.caption(organization.get("notes", ""))
    cols = st.columns(4)
    for col, report in zip(cols, council["specialists"]):
        with col:
            st.markdown(f"<div class='signal'><h4>{report['specialist']}</h4>", unsafe_allow_html=True)
            st.write(report["finding"])
            st.caption(f"Evidence: {_evidence_color(report['evidence'])} {report['evidence']}")
            st.markdown("</div>", unsafe_allow_html=True)
    chief = council["chief_strategy"]
    st.markdown("### Chief Strategy synthesis")
    m1, m2 = st.columns(2)
    m1.metric("Council evidence", chief["evidence"].title())
    m2.metric("Decision status", chief["decision_status"].replace("_", " ").title())
    st.info(chief["principle"])
    with st.expander("Full auditable council package", expanded=False):
        st.json(council)

elif page == "Context Matrix":
    st.markdown("## Time × Space Context Matrix")
    st.caption("Explore splits while protecting the user from tiny samples, multiple comparisons and confounding.")
    pitcher = st.selectbox("Pitcher", sorted(df.pitcher_name.unique()), key="context_pitcher")
    dimensions = available_dimensions(df)
    preferred = ["day_of_week", "home_away", "stand", "day_night", "days_rest", "venue", "opponent_team"]
    ordered = [d for d in preferred if d in dimensions] + [d for d in dimensions if d not in preferred]
    dimension = st.selectbox("Context dimension", ordered)
    table, warnings = context_split_table(df, pitcher, dimension)
    if table.empty:
        st.info("No context table could be produced for this data source.")
    else:
        st.plotly_chart(
            px.bar(
                table,
                x=dimension,
                y="posterior_value",
                hover_data=["n", "games", "avg_velocity", "whiff_rate", "hard_contact_rate", "evidence"],
                title=f"Shrunk defensive-value signal by {dimension}",
            ),
            use_container_width=True,
        )
        st.dataframe(table, use_container_width=True, hide_index=True)
    for warning in warnings:
        st.warning(warning["message"])

    matrix = context_matrix(df, pitcher, "home_away", "stand")
    if not matrix.empty:
        st.plotly_chart(
            px.imshow(matrix, text_auto=".3f", aspect="auto", title="Home/Away × Batter Side context matrix"),
            use_container_width=True,
        )
    st.info(
        "A Monday or Wednesday split is not a cause. PennantIQ ranks it as an exploratory signal until it remains stable after controlling for rest, opponent, park and role."
    )

elif page == "Shadow Mode":
    st.markdown("## Shadow Mode")
    st.caption("Replay history using only information available before each evaluation date.")
    bt, metrics = _shadow(df)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Evaluated pitches", f"{metrics['rows']:,}")
    m2.metric("Moderate/strong coverage", f"{metrics['coverage']:.1%}")
    m3.metric("Observed family matched", f"{metrics['followed_rate']:.1%}")
    m4.metric("Leakage policy", "Chronological")
    if not bt.empty:
        aggregate = bt.groupby("game_date", as_index=False).agg(
            observed_value=("observed_value", "mean"),
            followed_rate=("recommendation_followed", "mean"),
        )
        st.plotly_chart(
            px.line(aggregate, x="game_date", y=["observed_value", "followed_rate"], title="Shadow-mode trace"),
            use_container_width=True,
        )
        st.dataframe(bt.tail(150), use_container_width=True, hide_index=True)
        st.warning(metrics["warning"])
    st.markdown(
        "**What this proves:** the system can produce and preserve a recommendation without future leakage. "
        "**What it does not prove:** that a different historical pitch would certainly have produced a better result."
    )

elif page == "Ask PennantIQ":
    st.markdown("## Ask PennantIQ")
    st.caption("The LLM explains and orchestrates. Deterministic tools perform the statistics.")
    c1, c2 = st.columns(2)
    pitcher = c1.selectbox("Pitcher", sorted(df.pitcher_name.unique()), key="ask_pitcher")
    batter = c2.selectbox("Batter", sorted(df.batter_name.unique()), key="ask_batter")
    c3, c4 = st.columns(2)
    balls = c3.selectbox("Balls", [0, 1, 2, 3], key="ask_balls")
    strikes = c4.selectbox("Strikes", [0, 1, 2], index=2, key="ask_strikes")
    query = st.text_area(
        "Question",
        f"Build an evidence-backed {balls}-{strikes} plan for {pitcher} against {batter}. Explain uncertainty and the adaptation signal.",
    )
    if st.button("Generate decision brief", type="primary"):
        start = time.perf_counter()
        result = generate_answer(df, pitcher, batter, balls, strikes, query)
        latency = (time.perf_counter() - start) * 1000
        st.markdown(result["answer"])
        confidence = (result["brief"].get("plan_a") or {}).get("confidence", "insufficient")
        row_id = log_interaction(
            query, "matchup_plan", result["provider"], latency, confidence,
            bool(result["sources"]), result["brief"]["abstain"], result,
        )
        st.session_state["interaction_id"] = row_id
        st.session_state["last_brief"] = result["brief"]
        with st.expander("Evidence package", expanded=True):
            st.json(result["brief"])
            st.dataframe(pd.DataFrame(result["sources"]), use_container_width=True, hide_index=True)
    if "interaction_id" in st.session_state:
        c1, c2 = st.columns(2)
        if c1.button("Useful"):
            record_feedback(st.session_state["interaction_id"], 1); st.success("Feedback recorded")
        if c2.button("Not useful"):
            record_feedback(st.session_state["interaction_id"], -1); st.warning("Feedback recorded")

elif page == "Decision Ritual":
    st.markdown("## Decision Ritual")
    st.caption("Confidence comes from preparation, not certainty. Record intention, evidence, choice, outcome and lesson.")
    metrics = decision_metrics()
    c1, c2, c3 = st.columns(3)
    c1.metric("Decisions remembered", metrics["decisions"])
    c2.metric("Decisions closed", metrics["closed"])
    c3.metric("Learning-loop completion", f"{metrics['learning_rate']:.1%}")

    with st.form("decision_form"):
        decision_type = st.selectbox("Decision type", ["pregame_matchup", "starter_plan", "bullpen", "lineup", "other"])
        subject = st.text_input("Subject", "Series preparation")
        chosen = st.text_input("Chosen action")
        rationale = st.text_area("Why this action?", "State the evidence, the alternative rejected and the uncertainty accepted.")
        evidence = st.selectbox("Evidence strength", ["strong", "moderate", "weak", "insufficient"])
        confidence = st.slider("Human confidence — not win probability", 0, 100, 60) / 100
        submitted = st.form_submit_button("Commit decision to memory", type="primary")
        if submitted:
            if not chosen.strip():
                st.error("A chosen action is required.")
            else:
                decision_id = log_decision(
                    decision_type, chosen, rationale, evidence,
                    context={"data_mode": active_mode, "data_start": profile["start"], "data_end": profile["end"]},
                    options=[], subject=subject, confidence=confidence,
                )
                st.success(f"Decision #{decision_id} committed. Return after the game to close the learning loop.")

    journal = decisions()
    if journal.empty:
        st.info("No decisions have been recorded yet.")
    else:
        st.dataframe(journal, use_container_width=True, hide_index=True)
    st.markdown(
        """<div class="promise"><b>The mystique:</b> the team enters every game with a deliberate ritual—observe, challenge, choose, commit, replay, learn. <b>The discipline:</b> every conviction remains tied to evidence and can be audited afterward.</div>""",
        unsafe_allow_html=True,
    )

elif page == "Trust & Monitoring":
    st.markdown("## Trust Ledger & Monitoring")
    trust, monitor = st.tabs(["Trust Ledger", "Operational Monitoring"])
    with trust:
        st.json({
            "version": VERSION,
            "organization_context": organization,
            "data_profile": profile,
            "method": "Empirical-Bayes scenario ranking plus contextual descriptive analytics",
            "retrieval": "keyword + TF-IDF vector + hybrid + overlap reranking",
            "abstention": "minimum evidence policy",
            "causal_status": "associative; no causal or championship guarantee",
            "real_data_boundary": "frozen real game results plus user-downloaded pitch data; no unlicensed pitch data redistributed",
            "gcp_target": "Cloud Storage → BigQuery/Dataform → Vertex AI → Cloud Run → Monitoring/Looker",
        })
        st.markdown("### Known data gaps")
        st.write(profile["missing_context"] or "No standard context gaps detected.")
    with monitor:
        logs = interactions()
        if logs.empty:
            st.info("Generate a decision brief to populate monitoring.")
        else:
            a, b, c, d = st.columns(4)
            a.metric("Queries", len(logs))
            b.metric("Median latency", f"{logs.latency_ms.median():.0f} ms")
            c.metric("Positive feedback", int((logs.feedback == 1).sum()))
            d.metric("Abstention rate", f"{logs.abstained.mean():.1%}")
            st.plotly_chart(px.histogram(logs, x="provider", title="Provider usage"), use_container_width=True)
            st.plotly_chart(px.histogram(logs, x="confidence", title="Evidence strength"), use_container_width=True)
            st.plotly_chart(px.line(logs, x="id", y="latency_ms", title="Latency"), use_container_width=True)
            st.plotly_chart(px.histogram(logs, x="feedback", title="Feedback"), use_container_width=True)
            st.plotly_chart(px.histogram(logs, x="abstained", title="Abstention"), use_container_width=True)
            st.plotly_chart(px.histogram(logs, x="grounded", title="Grounded-answer signal"), use_container_width=True)
            st.dataframe(logs, use_container_width=True, hide_index=True)

elif page == "GCP Platform":
    st.markdown("## GCP Production Platform")
    st.caption("The local prototype is intentionally simple. The enterprise platform is explicitly designed for Google Cloud.")
    st.image(str(ROOT / "assets" / "gcp-architecture.svg"), use_container_width=True)
    st.markdown(
        """
**Why GCP:** the target combines BigQuery for large structured baseball data, Vertex AI for governed models and agents, Cloud Run for portable containers, and native observability. The repository includes optional adapters and Terraform blueprints; it does not pretend that an undeployed diagram is a production environment.

**Public prototype:** local CSV/DuckDB-compatible workflow, deterministic analytics and optional LLM.

**Private Team edition:** team-owned datasets, feature store, video/tracking connectors, access controls, decision memory and organization-specific models.
"""
    )
    st.code(
        "pip install -r requirements-gcp.txt\n"
        "gcloud auth application-default login\n"
        "terraform -chdir=infra/gcp init\n"
        "terraform -chdir=infra/gcp plan -var='project_id=YOUR_PROJECT'",
        language="bash",
    )
    st.info("Read docs/GCP_ARCHITECTURE.md and infra/gcp/README.md before provisioning resources.")

elif page == "Roadmap":
    roadmap = ROOT / "docs" / "ROADMAP.md"
    st.markdown(roadmap.read_text(encoding="utf-8"))
