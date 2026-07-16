from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import all models so Alembic can detect them
from app.models.organization import Organization, OrgMember  # noqa: E402, F401
from app.models.user import User  # noqa: E402, F401
from app.models.project import Project  # noqa: E402, F401
from app.models.worker import Worker  # noqa: E402, F401
from app.models.project_worker import ProjectWorker  # noqa: E402, F401
from app.models.evaluation import Evaluation  # noqa: E402, F401
from app.models.evaluation_audit import EvaluationAuditLog  # noqa: E402, F401
from app.models.worker_consent import WorkerConsent  # noqa: E402, F401
from app.models.subscription import Subscription, PaymentEvent  # noqa: E402, F401
from app.models.bot import BotConversation, BotInboundEvent, BotLead, BotMessage  # noqa: E402, F401
