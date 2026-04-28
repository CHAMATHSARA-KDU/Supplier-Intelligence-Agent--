# Supplier-Intelligence-Agent--
 Overview
The Supplier Intelligence Agent is a fully autonomous AI system that eliminates manual supplier due diligence in supply chain management. What traditionally takes procurement teams 2–3 weeks of manual research, this agent completes in under 60 seconds — automatically.
Given a single supplier name, the agent independently researches reputation, financial health, geo-political risks, and delivery performance using live web intelligence. It then scores the supplier, generates a professional PDF report, and emails it to the procurement manager — all without any human intervention.

 The Business Problem
Before signing any supplier contract, companies must conduct due diligence — a thorough background investigation covering:

Is the supplier reputable? Any complaints, scandals, or quality issues?
Are they financially stable? Any bankruptcy or insolvency risks?
Is their country safe? Any political instability, sanctions, or labour unrest?
Do they deliver reliably? Any history of delays or logistics failures?

For large companies evaluating dozens of suppliers annually, this process costs months of human effort and carries significant financial risk if the wrong supplier is chosen. Supply chain failures cost the global economy over $4 trillion annually.
This agent solves that problem with autonomous AI.

 Key Features
FeatureDescription Autonomous ReAct reasoningLangChain ReAct loop independently decides which tools to call and in what order 4-dimension researchSearches reputation, financial health, geo-political risk, and delivery track record Risk scoringScores suppliers 0–10 with LOW / MODERATE / HIGH / CRITICAL risk levels PDF report generationAutomatically generates a professional formatted intelligence report Email deliverySends PDF report to procurement manager via Gmail SMTP automatically Watchlist & rankingsSaves all suppliers, ranks them safest to riskiest with persistent storage Background monitoringAPScheduler re-evaluates all suppliers hourly with zero human input Conversation memoryRemembers previous evaluations across sessions for comparison queries Morning briefing alertsAutomatically flags suppliers whose risk score worsened since last check

 Architecture
User Query (Streamlit UI)
        ↓
LangChain ReAct Agent (Groq LLaMA 3)
        ↓ autonomously decides research order
  ┌─────┬──────────┬────────────┬──────────┐
  ↓     ↓          ↓            ↓          ↓
Reputation  Finance  Geo-risk  Delivery  Scorer
Search      Search   Search    Search    (0-10)
  └─────┴──────────┴────────────┴──────────┘
        ↓
Conversation Memory (LangChain Buffer)
        ↓
PDF Report (ReportLab) → Email (Gmail SMTP)
        ↓
Watchlist (JSON) → Rankings → Autonomous Recommendation
        ↓
Background Scheduler (APScheduler) — hourly re-evaluation

 Tech Stack
ComponentTechnologyAgent frameworkLangChain 0.2.16 (ReAct pattern)LLMGroq LLaMA 3.3 70B VersatileWeb intelligenceTavily API (live search)UIStreamlitPDF generationReportLabEmail deliveryGmail SMTPBackground schedulingAPSchedulerMemoryLangChain ConversationBufferMemoryData persistenceJSON watchlist

 Project Structure
supplier_agent_final/
│
├── app.py                    # Streamlit UI — main entry point
├── agent.py                  # LangChain ReAct agent + memory
├── scheduler.py              # Background autonomous re-evaluation
├── watchlist.py              # Supplier persistence + ranking
├── score_extractor.py        # Parses risk scores from agent output
├── pdf_report.py             # Professional PDF report generator
├── email_alert.py            # Gmail SMTP email with PDF attachment
├── requirements.txt          # All dependencies
├── install.bat               # One-click Windows installer
├── .env.example              # API key template
│
└── tools/
    ├── __init__.py
    ├── reputation_tool.py    # Searches reviews, complaints, quality
    ├── financial_tool.py     # Searches bankruptcy, stability, funding
    ├── geopolitical_tool.py  # Searches country risks, sanctions
    ├── delivery_tool.py      # Searches on-time rates, logistics
    └── scoring_tool.py       # Calculates 0–10 risk score

 Setup & Installation
Prerequisites

Python 3.10
A Gmail account with 2-Step Verification enabled

Step 1 — Clone the repository
bashgit clone https://github.com/YOUR_USERNAME/supplier-intelligence-agent.git
cd supplier-intelligence-agent
Step 2 — Install dependencies
Windows (one-click):
bashinstall.bat
Manual:
bashpip install -r requirements.txt
Step 3 — Get your API keys (all free)
KeyWhere to get itGroq API Keyhttps://console.groq.com → API Keys → CreateTavily API Keyhttps://app.tavily.com → free planGmail App Passwordhttps://myaccount.google.com/apppasswords
Step 4 — Run the app
bashstreamlit run app.py
Or on Windows with virtual environment:
bash.\venv\Scripts\python.exe -m streamlit run app.py
Step 5 — Enter keys in sidebar
Open http://localhost:8501 and paste your API keys in the sidebar.

 How to Use
Evaluate a supplier:
Evaluate DhakaTextiles Ltd — Bangladesh
Assess multiple suppliers:
Assess Shenzhen ElectroHub Co — China
Due diligence on Mumbai Pharma Exports — India
Compare suppliers:
Compare the two suppliers I just evaluated
After each evaluation the agent automatically:

Displays full intelligence report
Saves supplier to watchlist
Generates PDF report
Emails PDF to your Gmail
Updates autonomous rankings


 Risk Score Breakdown
ScoreLevelRecommendation0 – 2.9🟢 LOW RISKSafe to proceed with full contract3 – 4.9🟡 MODERATE RISKRequest trial order first5 – 6.9🔴 HIGH RISKSeek alternative suppliers7 – 10⛔ CRITICAL RISKDo not proceed — escalate immediately

 Why This is a Genuine Autonomous Agent
Unlike a simple chatbot, this agent:

Plans independently — decides which tools to call and in what order from a single query
Acts autonomously — calls 4+ tools in sequence without being told
Observes and reasons — analyses each tool result before deciding next step
Remembers — maintains conversation history for comparison queries
Monitors continuously — re-evaluates suppliers in background without human trigger
Takes proactive action — sends alerts and emails without being asked

This follows the ReAct (Reasoning + Acting) pattern — the industry standard for autonomous AI agents.

 Business Impact

 Time saved: 2–3 weeks → 60 seconds per supplier evaluation
 Cost reduced: Eliminates manual research labour costs
 Risk reduced: Catches financial, reputational, and geo-political red flags before contracts are signed
 Decision quality: Data-driven scoring replaces subjective human judgment
 Continuous protection: Hourly monitoring means risks are caught early, not after contracts are signed
