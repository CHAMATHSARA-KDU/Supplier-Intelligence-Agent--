"""
Streamlit UI: Supplier Intelligence Agent
Run with: streamlit run app.py
"""

import streamlit as st
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import create_agent
from watchlist import (
    save_to_watchlist,
    get_ranked_watchlist,
    detect_score_changes,
    remove_from_watchlist,
    load_watchlist,
)
from score_extractor import extract_score_from_output, extract_supplier_name
from scheduler import start_scheduler, get_scheduler_status
from pdf_report import generate_pdf_report
from email_alert import send_risk_alert_email

st.set_page_config(
    page_title="Supplier Intelligence Agent",
    page_icon="🔍",
    layout="wide",
)

st.markdown("""
<style>
  .alert-box {
    border-left: 4px solid #e74c3c;
    padding: 10px 14px;
    border-radius: 0 8px 8px 0;
    margin-bottom: 8px;
  }
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Configuration")

    groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...", key="groq_key_input")
    tavily_key = st.text_input("Tavily API Key", type="password", placeholder="tvly-...", key="tavily_key_input")

    if groq_key:
        st.session_state["groq_key"] = groq_key
    if tavily_key:
        st.session_state["tavily_key"] = tavily_key

    groq_key = st.session_state.get("groq_key", groq_key)
    tavily_key = st.session_state.get("tavily_key", tavily_key)

    st.divider()
    st.markdown("### 📧 Email alerts")
    alert_email = st.text_input("Your Gmail address", placeholder="yourname@gmail.com", key="alert_email_input")
    alert_password = st.text_input("Gmail App Password", type="password", placeholder="xxxx xxxx xxxx xxxx", key="alert_password_input", help="Google Account → Security → App Passwords")

    if alert_email:
        st.session_state["alert_email"] = alert_email
    if alert_password:
        st.session_state["alert_password"] = alert_password

    alert_email = st.session_state.get("alert_email", alert_email)
    alert_password = st.session_state.get("alert_password", alert_password)

    if alert_email and alert_password:
        os.environ["ALERT_EMAIL"] = alert_email
        os.environ["ALERT_EMAIL_PASSWORD"] = alert_password
        st.success("📧 Email alerts active")
    else:
        st.caption("Add Gmail details to receive PDF reports by email")

    st.divider()
    st.markdown("### 💡 Quick evaluate")
    examples = [
        "Evaluate DhakaTextiles Ltd — Bangladesh",
        "Assess Shenzhen ElectroHub Co — China",
        "Due diligence on Mumbai Pharma Exports — India",
        "Is VietGarment JSC — Vietnam reliable?",
    ]
    for q in examples:
        if st.button(q, use_container_width=True):
            st.session_state["prefill"] = q

    st.divider()
    status = get_scheduler_status()
    if status["running"]:
        st.success("✅ Autonomous scheduler running")
        if status["next_run"]:
            st.caption(f"⏰ Next auto-evaluation: {status['next_run']}")
    else:
        st.warning("Scheduler not started")

    wl = load_watchlist()
    if wl:
        latest = max([d.get("last_evaluated", "") for d in wl.values()], default="")
        if latest:
            st.caption(f"🔄 Last evaluated: {latest}")

    # Manual refresh button instead of auto-refresh
    if st.button("🔄 Refresh status", use_container_width=True):
        st.rerun()

    if st.button("🗑️ Clear conversation", use_container_width=True):
        st.session_state["messages"] = []
        st.session_state["agent"] = None
        st.rerun()

# ── API key guard ─────────────────────────────────────────────
if not groq_key or not tavily_key:
    st.title("🔍 Supplier Intelligence Agent")
    st.markdown("*Autonomous supplier due diligence powered by live web intelligence.*")
    st.warning("⬅️ Please enter your Groq and Tavily API keys in the sidebar to begin.")
    st.stop()

os.environ["GROQ_API_KEY"] = groq_key
os.environ["TAVILY_API_KEY"] = tavily_key

# ── Init agent ────────────────────────────────────────────────
if "agent" not in st.session_state or st.session_state["agent"] is None:
    with st.spinner("Initialising agent..."):
        try:
            st.session_state["agent"] = create_agent()
        except Exception as e:
            st.error(f"Failed to initialise agent: {e}")
            st.stop()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ── Start scheduler once ──────────────────────────────────────
if "scheduler_started" not in st.session_state:
    try:
        start_scheduler(interval_hours=1)
        st.session_state["scheduler_started"] = True
    except Exception:
        st.session_state["scheduler_started"] = False

# ── Morning briefing ──────────────────────────────────────────
try:
    alerts = detect_score_changes()
    if alerts:
        st.error(f"⚠️ Autonomous monitoring flagged {len(alerts)} risk change(s)!")
        with st.expander("📋 View morning briefing", expanded=True):
            for alert in alerts:
                delta = round(alert["current_score"] - alert["previous_score"], 1)
                st.markdown(
                    f"<div class='alert-box'>"
                    f"<strong>{alert['supplier']}</strong><br>"
                    f"Score: <strong>{alert['previous_score']} → {alert['current_score']}</strong>"
                    f" (+{delta}) — now <strong>{alert['risk_level']}</strong><br>"
                    f"<small>Last evaluated: {alert['last_evaluated']}</small>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        st.divider()
except Exception:
    pass

# ── Main UI ───────────────────────────────────────────────────
st.title("🔍 Supplier Intelligence Agent")
st.markdown("*Autonomous supplier due diligence — live web intelligence + AI reasoning + PDF reports.*")
st.divider()

tab1, tab2, tab3 = st.tabs(["💬 Evaluate supplier", "📋 Watchlist & rankings", "📁 Generated reports"])

# ── TAB 1: Chat ───────────────────────────────────────────────
with tab1:
    st.markdown("#### Supplier due diligence chat")
    st.caption("Type any supplier name — agent researches all dimensions, generates a PDF and emails it automatically.")

    # Display all previous messages
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            # Show download button for PDF if available
            if msg["role"] == "assistant" and "pdf_path" in msg:
                pdf_path = msg["pdf_path"]
                if os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="⬇️ Download PDF Report",
                            data=f,
                            file_name=os.path.basename(pdf_path),
                            mime="application/pdf",
                            key=f"dl_msg_{pdf_path}",
                        )

    prefill = st.session_state.pop("prefill", None)
    user_input = st.chat_input("Enter a supplier name or question...") or prefill

    if user_input:
        # Add user message
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Run agent and display response
        with st.chat_message("assistant"):
            with st.spinner("🔍 Agent is researching all risk dimensions... (this may take 30-60 seconds)"):
                try:
                    response = st.session_state["agent"].invoke({"input": user_input})
                    answer = response.get("output", "Sorry, could not generate a response.")
                except Exception as e:
                    answer = f"Error: {str(e)}"

            # Display the answer
            st.markdown(answer)

            # Generate PDF and send email
            pdf_path = None
            try:
                score, risk_level = extract_score_from_output(answer)
                if score is not None:
                    supplier_name = extract_supplier_name(user_input)

                    # Save to watchlist
                    previous = save_to_watchlist(
                        supplier_name=supplier_name,
                        score=score,
                        risk_level=risk_level,
                        summary=answer[:600],
                    )

                    if previous is not None:
                        delta = round(score - previous, 1)
                        direction = "worsened" if delta > 0 else "improved"
                        st.info(f"Watchlist updated — {supplier_name} score {direction} ({previous} → {score})")
                    else:
                        st.success(f"✅ Added to watchlist — {supplier_name} | {score}/10 | {risk_level}")

                    # Generate PDF
                    with st.spinner("📄 Generating PDF report..."):
                        try:
                            pdf_path = generate_pdf_report(
                                supplier_name=supplier_name,
                                score=score,
                                risk_level=risk_level,
                                summary=answer,
                            )
                            st.success(f"📄 PDF report generated!")

                            # Download button
                            with open(pdf_path, "rb") as f:
                                st.download_button(
                                    label="⬇️ Download PDF Report",
                                    data=f,
                                    file_name=os.path.basename(pdf_path),
                                    mime="application/pdf",
                                    key=f"dl_{supplier_name}_{score}",
                                )
                        except Exception as e:
                            st.warning(f"PDF generation issue: {str(e)}")

                    # Send email
                    a_email = os.getenv("ALERT_EMAIL")
                    a_password = os.getenv("ALERT_EMAIL_PASSWORD")
                    if a_email and a_password:
                        with st.spinner("📧 Sending PDF report by email..."):
                            try:
                                sent = send_risk_alert_email(
                                    sender_email=a_email,
                                    sender_password=a_password,
                                    receiver_email=a_email,
                                    supplier_name=supplier_name,
                                    previous_score=previous or score,
                                    current_score=score,
                                    risk_level=risk_level,
                                    summary=answer[:400],
                                    pdf_path=pdf_path,
                                )
                                if sent:
                                    st.success(f"📧 PDF report emailed to {a_email}!")
                                else:
                                    st.warning("Email sending failed. Check your Gmail App Password.")
                            except Exception as e:
                                st.warning(f"Email issue: {str(e)}")

            except Exception as e:
                pass

            # Save message with pdf_path
            st.session_state["messages"].append({
                "role": "assistant",
                "content": answer,
                "pdf_path": pdf_path or "",
            })

# ── TAB 2: Watchlist ──────────────────────────────────────────
with tab2:
    st.markdown("#### Supplier watchlist — ranked safest to riskiest")
    st.caption("Re-evaluated autonomously every 1 hour. PDF report generated and emailed on each evaluation.")

    try:
        ranked = get_ranked_watchlist()
    except Exception:
        ranked = []

    if not ranked:
        st.info("No suppliers yet. Evaluate one in the chat tab to add them.")
    else:
        scores = [d.get("score", 0) for _, d in ranked]
        risk_counts = {"LOW RISK": 0, "MODERATE RISK": 0, "HIGH RISK": 0, "CRITICAL RISK": 0}
        for _, d in ranked:
            lvl = d.get("risk_level", "")
            if lvl in risk_counts:
                risk_counts[lvl] += 1

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total suppliers", len(ranked))
        c2.metric("Low risk", risk_counts["LOW RISK"])
        c3.metric("High / Critical", risk_counts["HIGH RISK"] + risk_counts["CRITICAL RISK"])
        c4.metric("Avg score", round(sum(scores) / len(scores), 1) if scores else 0)

        st.divider()

        color_map = {
            "LOW RISK": "green",
            "MODERATE RISK": "orange",
            "HIGH RISK": "red",
            "CRITICAL RISK": "darkred",
        }

        for rank, (name, data) in enumerate(ranked, 1):
            score = data.get("score", "N/A")
            risk_level = data.get("risk_level", "UNKNOWN")
            last_eval = data.get("last_evaluated", "Unknown")
            prev_score = data.get("previous_score")
            summary = data.get("summary", "")

            change_str = ""
            if prev_score is not None and isinstance(score, float):
                delta = round(score - prev_score, 1)
                if delta > 0:
                    change_str = f" ↑ +{delta}"
                elif delta < 0:
                    change_str = f" ↓ {delta}"

            with st.expander(f"#{rank}  {name}  —  {score}/10  |  {risk_level}{change_str}  |  {last_eval}"):
                badge = color_map.get(risk_level, "gray")
                st.markdown(f"**Risk level:** :{badge}[{risk_level}]")
                st.markdown(f"**Score:** {score} / 10")
                if prev_score is not None:
                    st.markdown(f"**Previous score:** {prev_score}")
                st.markdown("**Summary:**")
                st.markdown(summary[:500] + "..." if len(summary) > 500 else summary)
                if st.button("Remove from watchlist", key=f"rm_{name}"):
                    remove_from_watchlist(name)
                    st.rerun()

        st.divider()
        st.markdown("#### Autonomous recommendation")
        best_name, best_data = ranked[0]
        st.success(f"**Safest to contract:** {best_name} — Score {best_data['score']}/10 ({best_data['risk_level']})")
        if len(ranked) > 1:
            worst_name, worst_data = ranked[-1]
            st.error(f"**Highest risk:** {worst_name} — Score {worst_data['score']}/10 ({worst_data['risk_level']})")

# ── TAB 3: Generated Reports ──────────────────────────────────
with tab3:
    st.markdown("#### Autonomously generated PDF reports")
    st.caption("Every evaluation automatically generates and saves a PDF report here.")

    reports_folder = "reports"
    if not os.path.exists(reports_folder):
        st.info("No reports generated yet. Evaluate a supplier to generate your first report.")
    else:
        report_files = sorted(
            [f for f in os.listdir(reports_folder) if f.endswith(".pdf")],
            reverse=True,
        )
        if not report_files:
            st.info("No reports generated yet. Evaluate a supplier to generate your first report.")
        else:
            st.success(f"📁 {len(report_files)} report(s) generated autonomously")
            for report_file in report_files:
                report_path = os.path.join(reports_folder, report_file)
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"📄 {report_file}")
                with col2:
                    with open(report_path, "rb") as f:
                        st.download_button(
                            label="Download",
                            data=f,
                            file_name=report_file,
                            mime="application/pdf",
                            key=f"dl_{report_file}",
                        )