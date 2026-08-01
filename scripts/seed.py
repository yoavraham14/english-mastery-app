"""
Seed the database with a starter vocabulary set.

Idempotent (safe to run repeatedly) - words already present are skipped, so this can
run on every deploy without creating duplicates.

Run locally:
    docker compose run --rm api python -m scripts.seed

In Kubernetes this becomes a Job - a one-shot workload that runs to completion rather
than staying alive like a Deployment. See labs.
"""

from sqlalchemy import select

from common.database import Base, SessionLocal, engine
from common.models import Word

# Vocabulary chosen for a DevOps engineer working in English:
# words that show up in documentation, incident reports, code review, and interviews.
WORDS = [
    ("ubiquitous", "נמצא בכל מקום", "Containers are now ubiquitous in modern infrastructure."),
    ("idempotent", "אידמפוטנטי - פעולה שחזרה עליה לא משנה את התוצאה", "Ansible tasks should be idempotent."),
    ("deprecate", "להוציא משימוש בהדרגה", "The v1 API was deprecated last year."),
    ("mitigate", "להקל, לצמצם נזק", "We added rate limiting to mitigate the abuse."),
    ("resilient", "עמיד, מתאושש מכשל", "A resilient system tolerates node failures."),
    ("throttle", "לחנוק, להגביל קצב", "The CPU was throttled once it hit the limit."),
    ("provision", "להקצות, להעמיד תשתית", "Terraform provisions the cluster."),
    ("reconcile", "ליישב - להביא מצב בפועל למצב הרצוי", "The controller reconciles actual state with desired state."),
    ("ephemeral", "זמני, בן חלוף", "Pod storage is ephemeral by default."),
    ("persist", "להישמר, להתמיד", "The data must persist across restarts."),
    ("contention", "תחרות על משאבים", "Disk contention slowed every query."),
    ("bottleneck", "צוואר בקבוק", "The database was the bottleneck, not the API."),
    ("granular", "מפורט, ברמת פירוט גבוהה", "RBAC allows granular permissions."),
    ("coarse", "גס, לא מפורט", "Cluster-admin is far too coarse a permission."),
    ("scope", "היקף, תחום", "The role is scoped to a single namespace."),
    ("delegate", "להאציל סמכות", "We delegate deployment to ArgoCD."),
    ("orchestrate", "לתזמר, לנהל מערכת מורכבת", "Kubernetes orchestrates containers across nodes."),
    ("converge", "להתכנס למצב יציב", "The rollout converged after two minutes."),
    ("diverge", "לסטות, להתפצל", "The cluster state diverged from Git."),
    ("drift", "סטייה הדרגתית מהמצב המוגדר", "Manual changes cause configuration drift."),
    ("audit", "ביקורת, בדיקה", "Every API call is written to the audit log."),
    ("enforce", "לאכוף", "Network policies enforce traffic rules."),
    ("bypass", "לעקוף", "Never bypass the review process."),
    ("escalate", "להסלים, להעביר לדרג גבוה יותר", "Escalate the incident if it is not resolved in an hour."),
    ("triage", "מיון לפי דחיפות", "The on-call engineer triages alerts."),
    ("remediate", "לתקן תקלה", "The script remediates the misconfiguration automatically."),
    ("rollback", "חזרה לגרסה קודמת", "We rolled back after the error rate spiked."),
    ("regression", "נסיגה - תקלה שחוזרת", "The release introduced a performance regression."),
    ("flaky", "לא יציב, נכשל באקראי", "That test is flaky and fails once in ten runs."),
    ("brittle", "שביר, נשבר בקלות", "The pipeline is brittle and breaks on any rename."),
    ("robust", "חסון, יציב", "A robust retry policy handles transient failures."),
    ("transient", "חולף, זמני", "The error was transient and cleared on retry."),
    ("stale", "מיושן, לא עדכני", "The cache returned stale data."),
    ("propagate", "להתפשט, לעבור הלאה", "The config change propagates to all replicas."),
    ("cascade", "מפל - כשל שגורר כשלים נוספים", "One slow service caused a cascading failure."),
    ("saturate", "להרוות, להגיע לרוויה", "The network link was saturated during the backup."),
    ("arbitrary", "שרירותי, לא מבוסס", "Do not pick an arbitrary memory limit."),
    ("deterministic", "דטרמיניסטי - אותו קלט נותן תמיד אותה תוצאה", "Builds should be deterministic and reproducible."),
    ("reproducible", "ניתן לשחזור", "A reproducible build produces identical output."),
    ("immutable", "בלתי ניתן לשינוי", "Container images are immutable once built."),
    ("mutable", "ניתן לשינוי", "ConfigMaps are mutable, images are not."),
    ("atomic", "אטומי - הכל או כלום", "The upgrade is atomic: it fully succeeds or fully rolls back."),
    ("graceful", "מסודר, הדרגתי", "A graceful shutdown drains connections first."),
    ("drain", "לרוקן", "Drain the node before maintenance."),
    ("evict", "לפנות, לגרש", "The kubelet evicts pods under memory pressure."),
    ("preempt", "להקדים ולתפוס מקום", "High-priority pods can preempt lower-priority ones."),
    ("quota", "מכסה", "The namespace has a CPU quota."),
    ("overhead", "תקורה - עלות נלווית", "Sidecars add memory overhead to every pod."),
    ("latency", "השהיה, זמן תגובה", "P99 latency rose to two seconds."),
    ("throughput", "תפוקה", "Throughput doubled after adding replicas."),
    ("verbose", "מפורט מדי, ארכני", "Enable verbose logging only while debugging."),
    ("concise", "תמציתי", "Write concise commit messages."),
    ("ambiguous", "דו-משמעי, לא ברור", "The error message was ambiguous."),
    ("explicit", "מפורש", "Be explicit about resource requests."),
    ("implicit", "משתמע, לא נאמר במפורש", "There is an implicit dependency on DNS."),
    ("redundant", "מיותר, או כפול לצורך גיבוי", "Redundant replicas survive a node failure."),
    ("obsolete", "מיושן, לא רלוונטי עוד", "That runbook is obsolete."),
    ("prerequisite", "תנאי מוקדם", "A running cluster is a prerequisite for this lab."),
    ("caveat", "הסתייגות, אזהרה", "One caveat: this only works on Linux nodes."),
    ("trade-off", "פשרה בין שתי אפשרויות", "There is a trade-off between cost and redundancy."),
    ("leverage", "לנצל, למנף", "Leverage caching to reduce database load."),
    ("streamline", "לייעל, לפשט", "We streamlined the release process."),
    ("consolidate", "לאחד, לרכז", "Consolidate the three scripts into one."),
    ("decouple", "לנתק תלות בין רכיבים", "The queue decouples the API from the worker."),
    ("bespoke", "מותאם אישית", "Avoid bespoke tooling when a standard exists."),
    ("pragmatic", "מעשי, ענייני", "A pragmatic fix beats a perfect one that ships late."),
    ("scrutinize", "לבחון בקפדנות", "Scrutinize every change to production config."),
    ("negligible", "זניח", "The performance cost was negligible."),
    ("supersede", "להחליף, לבוא במקום", "The new policy supersedes the old one."),
    ("mandate", "לחייב, להורות", "The security team mandates image scanning."),

    # Batch 2
    ("instantiate", "ליצור מופע, להקים", "Terraform instantiates the resources defined in the plan."),
    ("invoke", "להפעיל, לקרוא לפונקציה", "The webhook invokes a Lambda function on every push."),
    ("paradigm", "פרדיגמה - מודל חשיבה מקובל", "Microservices are a different paradigm than a monolith."),
    ("monolith", "מונוליט - יישום גדול ומאוחד", "Breaking the monolith into services took two years."),
    ("abstraction", "הפשטה - הסתרת פרטים מיותרים", "Kubernetes is an abstraction over raw containers."),
    ("primitive", "רכיב בסיסי, יסודי", "A Pod is the most basic primitive in Kubernetes."),
    ("anomaly", "חריגה, סטייה מהרגיל", "The monitoring system flagged an anomaly in request latency."),
    ("heuristic", "היוריסטי - כלל אצבע מעשי", "The autoscaler uses a simple heuristic based on CPU usage."),
    ("deterministic", "דטרמיניסטי", "Hashing the input gives a deterministic output every time."),
    ("asynchronous", "אסינכרוני - לא ממתין לתשובה מיידית", "The worker processes tasks asynchronously."),
    ("synchronous", "סינכרוני - ממתין לתשובה לפני שממשיך", "A synchronous call blocks until the response arrives."),
    ("concurrency", "מקביליות - ריצה של כמה תהליכים בו זמנית", "Concurrency bugs are notoriously hard to reproduce."),
    ("parallelism", "מקביליות אמיתית על מספר ליבות", "Parallelism speeds up the batch job across CPU cores."),
    ("race condition", "מצב מרוץ - תוצאה תלוית תזמון", "Two goroutines writing the same variable caused a race condition."),
    ("deadlock", "מבוי סתום - שני תהליכים חוסמים זה את זה", "The two services entered a deadlock waiting on each other."),
    ("starvation", "הרעבה - תהליך שלא מקבל משאבים", "Low-priority jobs suffered starvation under heavy load."),
    ("checksum", "סכום ביקורת - ערך לאימות שלמות הנתונים", "The download failed the checksum verification."),
    ("integrity", "שלמות, יושרה", "Data integrity is checked before the migration runs."),
    ("provenance", "מקור, שרשרת מוצא", "Image provenance is verified before deployment."),
    ("attestation", "אישור, הצהרה מאומתת", "The pipeline generates a build attestation."),
    ("tamper", "לשבש, להתערב באופן זדוני", "The signature prevents the artifact from being tampered with."),
    ("exploit", "לנצל פרצת אבטחה", "The vulnerability could be exploited remotely."),
    ("patch", "תיקון תוכנה", "Apply the security patch before the weekend."),
    ("harden", "לחזק, לאבטח מערכת", "Harden the image by removing unused packages."),
    ("footprint", "טביעת רגל - היקף המשאבים או השטח", "A smaller image has a smaller attack footprint."),
    ("baseline", "קו בסיס - מצב ייחוס להשוואה", "Compare current latency against last month's baseline."),
    ("benchmark", "מדד השוואה, מבחן ביצועים", "We ran a benchmark before and after the optimization."),
    ("regression test", "בדיקת נסיגה", "Regression tests catch bugs reintroduced by new code."),
    ("smoke test", "בדיקת עשן - בדיקה בסיסית ומהירה", "A smoke test confirms the service starts up correctly."),
    ("canary", "קנרית - פריסה הדרגתית לקבוצה קטנה", "We roll out to a canary group before full deployment."),
    ("blue-green", "פריסת כחול-ירוק - שתי סביבות מקבילות להחלפה חלקה", "Blue-green deployment allows an instant rollback."),
    ("feature flag", "דגל תכונה - מתג להפעלה/כיבוי תכונה", "The new UI is hidden behind a feature flag."),
    ("toggle", "מתג, להחליף מצב", "Toggle the flag to enable the beta feature."),
    ("instrument", "להוסיף כלי מדידה לקוד", "Instrument the API to expose request metrics."),
    ("telemetry", "טלמטריה - נתוני ניטור הנאספים מרחוק", "Telemetry from the agents feeds the central dashboard."),
    ("aggregate", "לצבור, לסכם נתונים", "Logs are aggregated into a single searchable index."),
    ("correlate", "למצוא קשר בין נתונים", "Correlate the error spike with the last deployment."),
    ("root cause", "סיבת שורש", "The root cause was a misconfigured timeout."),
    ("workaround", "פתרון עוקף, פתרון זמני", "We shipped a workaround until the real fix is ready."),
    ("stopgap", "פתרון ביניים זמני", "The stopgap kept the service up for another week."),
    ("technical debt", "חוב טכני - פשרות שדוחות בעיות לעתיד", "Skipping tests now creates technical debt later."),
    ("refactor", "לשכתב קוד מבלי לשנות התנהגות", "We refactored the module to remove duplication."),
    ("legacy", "מערכת ישנה, ירושה טכנולוגית", "The legacy system still processes nightly batches."),
    ("greenfield", "פרויקט חדש לגמרי, ללא מגבלות ישנות", "This is a greenfield project with no legacy constraints."),
    ("brownfield", "פרויקט הנבנה על מערכת קיימת", "Migrating a brownfield system is slower than starting fresh."),
    ("onboarding", "קליטה, תהליך הצטרפות", "New engineers go through a two-week onboarding."),
    ("handoff", "מסירה, העברת אחריות", "The on-call handoff happens every Monday morning."),
    ("runbook", "מדריך תפעולי לשעת תקלה", "Follow the runbook when the disk usage alert fires."),
    ("postmortem", "ניתוח לאחר תקלה", "We write a blameless postmortem after every incident."),
    ("blameless", "ללא האשמה אישית", "A blameless culture encourages honest incident reports."),
    ("accountability", "אחריותיות", "Clear ownership improves accountability for services."),
    ("ownership", "בעלות, אחריות על רכיב", "Each team has ownership of its own microservice."),
    ("stakeholder", "בעל עניין", "Notify all stakeholders before the maintenance window."),
    ("maintenance window", "חלון תחזוקה", "The upgrade is scheduled for the maintenance window."),
    ("downtime", "זמן השבתה", "The migration caused ten minutes of downtime."),
    ("uptime", "זמן פעילות רציף", "The service maintained 99.9% uptime last quarter."),
    ("threshold", "סף", "An alert fires once CPU crosses the threshold."),
    ("baseline drift", "סטייה מקו הבסיס לאורך זמן", "Baseline drift made the old alert thresholds useless."),
    ("noise", "רעש - התראות לא רלוונטיות", "Too much alert noise causes people to ignore pages."),
    ("signal", "אות, מידע רלוונטי", "Filter out noise so the real signal stands out."),
    ("pager fatigue", "עייפות מהתראות", "Pager fatigue leads engineers to miss real incidents."),
    ("on-call", "כונן, זמין לתקלות", "She is on-call this week for the platform team."),
    ("sunset", "להוציא משימוש לצמיתות", "The old API will be sunset by the end of the year."),
    ("backfill", "מילוי רטרואקטיבי של נתונים", "We ran a backfill job to populate historical records."),
    ("snapshot", "תמונת מצב", "Take a snapshot of the volume before the upgrade."),
    ("checkpoint", "נקודת ביקורת, שמירת מצב ביניים", "The job resumes from the last checkpoint after a crash."),
    ("quorum", "קוורום - מספר מינימלי להסכמה", "etcd requires a quorum of nodes to accept a write."),
    ("consensus", "קונצנזוס - הסכמה בין צמתים", "Raft is a consensus algorithm used by etcd."),
    ("split-brain", "מוח מפוצל - שני חלקי מערכת פועלים בנפרד", "A network partition can cause a split-brain scenario."),
    ("partition", "חלוקה, ניתוק רשת", "A network partition isolated half the cluster nodes."),
    ("failover", "מעבר לגיבוי בעת כשל", "Failover to the standby database took under a minute."),
    ("standby", "במצב המתנה, גיבוי", "The standby replica is promoted if the primary fails."),
    ("promote", "לקדם, להעלות בדרגה", "Promote the read replica to primary during failover."),
    ("demote", "להוריד בדרגה", "The old primary is demoted to a replica after recovery."),
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    added = 0
    skipped = 0
    try:
        for word, translation, sentence in WORDS:
            exists = db.execute(select(Word).where(Word.word == word)).scalars().first()
            if exists:
                skipped += 1
                continue
            db.add(
                Word(
                    word=word,
                    translation=translation,
                    example_sentence=sentence,
                )
            )
            added += 1
        db.commit()
    finally:
        db.close()

    print(f"Seed complete: {added} added, {skipped} already present.")


if __name__ == "__main__":
    seed()
