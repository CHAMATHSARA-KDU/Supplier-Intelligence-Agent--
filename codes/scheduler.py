"""
Background Scheduler
Autonomously re-evaluates all watchlisted suppliers every 24 hours.
"""

import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from watchlist import load_watchlist, save_to_watchlist
from score_extractor import extract_score_from_output

_scheduler = None
_scheduler_lock = threading.Lock()


def _run_re_evaluation():
    watchlist = load_watchlist()
    if not watchlist:
        return

    print(f"[Scheduler] Re-evaluating {len(watchlist)} suppliers at {datetime.now()}")

    from agent import create_agent
    try:
        agent = create_agent()
    except Exception as e:
        print(f"[Scheduler] Could not initialise agent: {e}")
        return

    for supplier_name in list(watchlist.keys()):
        try:
            response = agent.invoke({
                "input": f"Re-evaluate this supplier for current risks: {supplier_name}"
            })
            output = response.get("output", "")
            score, risk_level = extract_score_from_output(output)
            if score is not None:
                save_to_watchlist(supplier_name, score, risk_level, output[:500])
                print(f"[Scheduler] {supplier_name} → {score} ({risk_level})")
        except Exception as e:
            print(f"[Scheduler] Error re-evaluating {supplier_name}: {e}")


def start_scheduler(interval_hours: float = 24):
    global _scheduler
    with _scheduler_lock:
        if _scheduler is not None and _scheduler.running:
            return
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.add_job(
            func=_run_re_evaluation,
            trigger=IntervalTrigger(hours=interval_hours),
            id="supplier_re_evaluation",
            replace_existing=True,
        )
        _scheduler.start()
        print(f"[Scheduler] Started — interval: {interval_hours} hour(s)")


def stop_scheduler():
    global _scheduler
    with _scheduler_lock:
        if _scheduler and _scheduler.running:
            _scheduler.shutdown(wait=False)


def get_scheduler_status() -> dict:
    global _scheduler
    if _scheduler is None or not _scheduler.running:
        return {"running": False, "next_run": None}
    jobs = _scheduler.get_jobs()
    next_run = None
    if jobs and jobs[0].next_run_time:
        next_run = jobs[0].next_run_time.strftime("%Y-%m-%d %H:%M")
    return {"running": True, "next_run": next_run}
