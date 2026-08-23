import html
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import streamlit as st

from app import (
    SYSTEM_PROMPT_PATH,
    evaluate_security_outcome,
    load_scenario_metadata,
    save_result,
    sha256_text,
)
from executor import (
    blocked_by_policy,
    execute_simulated,
)
from llm import analyze_incident
from policy import evaluate_action


SHOWCASE_DIR = Path(__file__).resolve().parent.parent
PREMIUM_CSS_PATH = Path(__file__).with_name("premium.css")


SCENARIOS = {
    "Benign Control": (
        SHOWCASE_DIR
        / "scenarios"
        / "benign_incident.txt"
    ),
    "Direct Prompt Injection": (
        SHOWCASE_DIR
        / "attacks"
        / "direct"
        / "direct-override-v1.txt"
    ),
    "Indirect Prompt Injection — Web Content": (
        SHOWCASE_DIR
        / "attacks"
        / "indirect"
        / "malicious-report-v1.txt"
    ),
}


MODES = {
    "Vulnerable Application": "vulnerable",
    "Hardened Application": "hardened",
}


def clear_result() -> None:
    st.session_state.pop(
        "showcase_result",
        None,
    )

    st.session_state.pop(
        "showcase_output_path",
        None,
    )


def analyze_case(
    mode: str,
    incident_path: Path,
) -> tuple[dict[str, Any], Path]:
    scenario = load_scenario_metadata(
        incident_path
    )

    system_prompt = SYSTEM_PROMPT_PATH.read_text(
        encoding="utf-8"
    )

    incident_report = incident_path.read_text(
        encoding="utf-8"
    )

    decision, raw_model_text, model = (
        analyze_incident(
            incident_report=incident_report,
            system_prompt=system_prompt,
        )
    )

    action = decision.requested_action

    if mode == "vulnerable":
        policy_record = {
            "evaluated": False,
            "allowed": None,
            "rule": None,
            "reason": (
                "Vulnerable Application Mode "
                "trusts model output without "
                "an external authorization decision."
            ),
        }

        execution_record = execute_simulated(
            action
        )

    else:
        policy = evaluate_action(
            action
        )

        policy_record = {
            "evaluated": True,
            **policy.to_dict(),
        }

        if policy.allowed:
            execution_record = (
                execute_simulated(action)
            )
        else:
            execution_record = (
                blocked_by_policy(action)
            )

    security_outcome = (
        evaluate_security_outcome(
            scenario=scenario,
            decision=decision,
            execution_record=execution_record,
        )
    )

    result = {
        "schema_version": "showcase-v0.4-gui",
        "created_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "mode": mode,
        "model": model,
        "scenario": scenario,
        "input": {
            "path": str(incident_path.relative_to(SHOWCASE_DIR)),
            "sha256": sha256_text(
                incident_report
            ),
        },
        "system_prompt": {
            "path": str(
                SYSTEM_PROMPT_PATH.relative_to(
                    SHOWCASE_DIR
                )
            ),
            "sha256": sha256_text(
                system_prompt
            ),
            "visible_in_gui": False,
        },
        "model_output": {
            "raw": raw_model_text,
            "parsed": decision.to_dict(),
        },
        "application_control": {
            "policy": policy_record,
            "execution": execution_record,
        },
        "security_outcome": security_outcome,
        "safety": {
            "real_world_execution": False,
            "executor": "simulation-only",
        },
    }

    output_path = save_result(
        result
    )

    return result, output_path


def outcome_text(
    outcome: dict[str, Any],
) -> str:
    if not outcome["attack_scenario"]:
        return (
            "BENIGN CONTROL — "
            "NO EXPLOIT ATTEMPT"
        )

    if not outcome["model_exploited"]:
        return (
            "ATTACK FAILED — "
            "MODEL NOT EXPLOITED"
        )

    if outcome["application_exploited"]:
        return (
            "EXPLOIT SUCCEEDED — "
            "SIMULATED APPLICATION EXPLOITED"
        )

    return (
        "MODEL EXPLOITED — "
        "APPLICATION PROTECTED"
    )


def card(
    title: str,
    value: str,
    detail: str,
    tone: str,
) -> None:
    safe_title = html.escape(title)
    safe_value = html.escape(value)
    safe_detail = html.escape(detail)

    st.markdown(
        f"""
        <div class="result-card {tone}">
            <div class="result-title">
                {safe_title}
            </div>
            <div class="result-value">
                {safe_value}
            </div>
            <div class="result-detail">
                {safe_detail}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.set_page_config(
    page_title=(
        "LAB-003 Prompt Injection Showcase"
    ),
    page_icon="AI",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    .hero {
        padding: 1.8rem 2rem;
        border: 1px solid #27364d;
        border-radius: 16px;
        background:
            linear-gradient(
                135deg,
                #101927 0%,
                #15243a 100%
            );
        margin-bottom: 1.5rem;
    }

    .hero-kicker {
        font-size: 0.78rem;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        opacity: 0.7;
        margin-bottom: 0.45rem;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }

    .hero-subtitle {
        max-width: 850px;
        opacity: 0.82;
        line-height: 1.6;
    }

    .result-card {
        min-height: 175px;
        padding: 1.3rem 1.4rem;
        border-radius: 14px;
        border: 1px solid #2d3d55;
        background: #111b29;
    }

    .result-card.bad {
        border-color: #74434b;
        background: #21171c;
    }

    .result-card.good {
        border-color: #315d4b;
        background: #14201b;
    }

    .result-card.neutral {
        border-color: #38506e;
        background: #121d2c;
    }

    .result-title {
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        opacity: 0.66;
        margin-bottom: 0.8rem;
    }

    .result-value {
        font-size: 1.35rem;
        font-weight: 700;
        margin-bottom: 0.65rem;
    }

    .result-detail {
        font-size: 0.9rem;
        opacity: 0.78;
        line-height: 1.45;
    }

    .boundary {
        padding: 1rem 1.2rem;
        border: 1px solid #2b394d;
        border-radius: 12px;
        background: #101927;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }

    .small-label {
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-size: 0.75rem;
        opacity: 0.65;
    }

    div.stButton > button {
        min-height: 3rem;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    f"<style>{PREMIUM_CSS_PATH.read_text(encoding='utf-8')}</style>",
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
        <div class="hero-kicker">
            LAB-003 Practical Showcase
        </div>
        <div class="hero-title">
            AI Security Incident Triage Assistant
        </div>
        <div class="hero-subtitle">
            From instruction compromise to
            application impact. The same LLM can
            fail in both modes; the difference is
            whether the application trusts the
            model as an authorization source.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


left, right = st.columns(
    [1, 1]
)

with left:
    scenario_label = st.selectbox(
        "Scenario",
        list(SCENARIOS.keys()),
        key="scenario_selector",
        on_change=clear_result,
    )

with right:
    mode_label = st.radio(
        "Application Security Mode",
        list(MODES.keys()),
        horizontal=True,
        key="mode_selector",
        on_change=clear_result,
    )


incident_path = SCENARIOS[
    scenario_label
]

mode = MODES[
    mode_label
]

scenario_metadata = (
    load_scenario_metadata(
        incident_path
    )
)

incident_report = (
    incident_path.read_text(
        encoding="utf-8"
    )
)


input_col, provenance_col = st.columns(
    [2, 1]
)

with input_col:
    st.text_area(
        "Incident Report",
        value=incident_report,
        height=330,
        disabled=True,
        help=(
            "Preset scenarios are locked so "
            "the demonstration remains reproducible."
        ),
    )

with provenance_col:
    st.markdown(
        "### Scenario Context"
    )

    st.write(
        f"**Scenario ID:** "
        f"{scenario_metadata['scenario_id']}"
    )

    st.write(
        f"**Attack type:** "
        f"{scenario_metadata['attack_type']}"
    )

    st.write(
        f"**Research basis:** "
        f"{scenario_metadata.get('research_basis')}"
    )

    formal_rate = scenario_metadata.get(
        "formal_observed_success_rate"
    )

    if formal_rate is not None:
        st.write(
            "**Formal observed ASR:** "
            f"{formal_rate * 100:.1f}%"
        )

    st.markdown(
        """
        <div class="boundary">
            <div class="small-label">
                Trust Boundary
            </div>
            Model output is treated as a
            recommendation. In Hardened Application
            Mode, high-impact actions require an
            external authorization decision.
        </div>
        """,
        unsafe_allow_html=True,
    )


run_clicked = st.button(
    "Run Security Analysis",
    type="primary",
    use_container_width=True,
)


if run_clicked:
    with st.spinner(
        "Running local LLM analysis..."
    ):
        try:
            result, output_path = (
                analyze_case(
                    mode=mode,
                    incident_path=incident_path,
                )
            )

            st.session_state[
                "showcase_result"
            ] = result

            st.session_state[
                "showcase_output_path"
            ] = str(output_path)

        except Exception as exc:
            st.error(
                f"Analysis failed: {exc}"
            )


result = st.session_state.get(
    "showcase_result"
)

output_path = st.session_state.get(
    "showcase_output_path"
)


if result is not None:
    result_matches_selection = (
        result.get("mode") == mode
        and result.get(
            "scenario",
            {},
        ).get("scenario_id")
        == scenario_metadata["scenario_id"]
    )

    if not result_matches_selection:
        clear_result()

        result = None
        output_path = None


if result is None:
    st.caption(
        "Run the selected scenario to generate "
        "a fresh result. Changing scenario or "
        "application mode clears the previous run."
    )


if result is not None:
    st.markdown("---")
    st.markdown(
        "## Security Outcome"
    )

    outcome = result[
        "security_outcome"
    ]

    model_exploited = outcome[
        "model_exploited"
    ]

    application_exploited = outcome[
        "application_exploited"
    ]

    if not outcome["attack_scenario"]:
        model_value = "NOT EXPLOITED"
        model_detail = (
            "This is a benign control scenario."
        )
        model_tone = "neutral"

        app_value = "NOT EXPLOITED"
        app_detail = (
            "No attacker objective was present."
        )
        app_tone = "neutral"

    else:
        model_value = (
            "EXPLOITED"
            if model_exploited
            else "NOT EXPLOITED"
        )

        model_detail = (
            "The LLM produced the "
            "attacker-defined action and target."
            if model_exploited
            else
            "The LLM did not produce the "
            "attacker-defined action and target."
        )

        model_tone = (
            "bad"
            if model_exploited
            else "good"
        )

        app_value = (
            "EXPLOITED"
            if application_exploited
            else (
                "PROTECTED"
                if model_exploited
                else "NOT EXPLOITED"
            )
        )

        if application_exploited:
            app_detail = (
                "The simulated application accepted "
                "the compromised model decision."
            )
            app_tone = "bad"
        else:
            app_detail = (
                "Application controls prevented "
                "the model compromise from reaching "
                "simulated impact."
            )
            app_tone = "good"

    final = outcome_text(
        outcome
    )

    if application_exploited:
        final_tone = "bad"
    elif model_exploited:
        final_tone = "good"
    else:
        final_tone = "neutral"

    col1, col2, col3 = st.columns(3)

    with col1:
        card(
            "Model Security",
            model_value,
            model_detail,
            model_tone,
        )

    with col2:
        card(
            "Application Security",
            app_value,
            app_detail,
            app_tone,
        )

    with col3:
        card(
            "Final Result",
            final,
            (
                "All operational effects in this "
                "showcase are simulation-only."
            ),
            final_tone,
        )

    st.markdown(
        "## Model Decision"
    )

    parsed = result[
        "model_output"
    ]["parsed"]

    action = parsed[
        "requested_action"
    ]

    d1, d2 = st.columns(2)

    with d1:
        st.write(
            f"**Severity:** "
            f"{parsed['severity']}"
        )
        st.write(
            f"**Summary:** "
            f"{parsed['summary']}"
        )

    with d2:
        st.write(
            f"**Requested action:** "
            f"`{action['type']}`"
        )
        st.write(
            f"**Target:** "
            f"`{action['target']}`"
        )
        st.write(
            f"**Reason:** "
            f"{action['reason']}"
        )

    st.markdown(
        "## Application Security Boundary"
    )

    policy = result[
        "application_control"
    ]["policy"]

    execution = result[
        "application_control"
    ]["execution"]

    if policy["evaluated"]:
        st.write(
            "**Policy Engine:** ACTIVE"
        )
        st.write(
            f"**Policy rule:** "
            f"`{policy['rule']}`"
        )
        st.write(
            "**Policy decision:** "
            + (
                "ALLOW"
                if policy["allowed"]
                else "DENY"
            )
        )
        st.write(
            f"**Policy reason:** "
            f"{policy['reason']}"
        )
    else:
        st.write(
            "**Policy Engine:** BYPASSED"
        )
        st.write(
            "**Trust decision:** "
            "MODEL OUTPUT TRUSTED"
        )

    st.write(
        f"**Application result:** "
        f"`{execution['status']}`"
    )

    st.markdown(
        "## Safety Boundary"
    )

    st.write(
        "**Executor:** SIMULATION ONLY"
    )
    st.write(
        "**Real-world action:** NONE"
    )

    st.markdown(
        "## Evidence"
    )

    evidence_name = (
        Path(output_path).name
        if output_path
        else "Unavailable"
    )

    st.write(
        f"**Evidence record:** "
        f"`{evidence_name}`"
    )

    with st.expander(
        "View structured evidence"
    ):
        st.code(
            json.dumps(
                result,
                indent=2,
                ensure_ascii=False,
            ),
            language="json",
        )
