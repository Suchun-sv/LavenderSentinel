# src/scheduler/scheduler_service.py

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from src.config import Config
from src.jobs.daily_arxiv import run_daily_arxiv_job


class SchedulerService:
    """
    Long-running scheduler service.

    - Starts APScheduler
    - Loads jobs from settings.yaml
    - Supports hot reload (no restart)
    """

    def __init__(self):
        self.scheduler = BackgroundScheduler(
            timezone=Config.scheduler.timezone
        )
        self._started = False

    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    def start(self) -> None:
        """
        Start scheduler (idempotent).
        """
        if self._started:
            return

        if not Config.scheduler.enabled:
            print("⏸ Scheduler disabled by config")
            return

        print("⏱ Starting SchedulerService...")
        self.scheduler.start()
        self.reload()
        self._started = True

    def shutdown(self) -> None:
        """
        Graceful shutdown.
        """
        if not self._started:
            return

        print("🛑 Stopping SchedulerService...")
        self.scheduler.shutdown(wait=False)
        self._started = False

    # --------------------------------------------------
    # Reload logic
    # --------------------------------------------------

    def reload(self) -> None:
        """
        Reload all jobs from config.

        Safe to call multiple times.
        """
        print("🔄 Reloading scheduler jobs...")

        self.scheduler.remove_all_jobs()

        self._add_daily_arxiv(job_id="daily_arxiv", cron_expr=Config.scheduler.daily_arxiv_job)

        self._log_jobs()

    # --------------------------------------------------
    # Job registration
    # --------------------------------------------------

    def _add_daily_arxiv(self, job_id: str, cron_expr: str) -> None:
        """
        Register daily_arxiv job.
        """
        trigger = CronTrigger.from_crontab(cron_expr)

        self.scheduler.add_job(
            run_daily_arxiv_job,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            max_instances=1,
            coalesce=True,
            misfire_grace_time=300,
        )

        print(f"✅ Job registered: {job_id} ({cron_expr})")

    # --------------------------------------------------
    # Debug helpers
    # --------------------------------------------------

    def _log_jobs(self) -> None:
        jobs = self.scheduler.get_jobs()
        if not jobs:
            print("⚠️ No scheduled jobs")
            return

        print("📅 Active jobs:")
        for job in jobs:
            print(f"  - {job.id} | next run at {job.next_run_time}")