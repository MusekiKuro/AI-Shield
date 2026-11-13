"""Public wire contracts. Monetary decisions belong to server services."""

from typing import Annotated, Literal

from pydantic import (
    AwareDatetime, BaseModel, ConfigDict, Field, StringConstraints,
    field_serializer, model_validator,
)

Language = Literal["ru", "kk"]
DialogueLanguage = Literal["ru", "kk", "mixed"]
Speaker = Literal["caller", "customer", "unknown"]
Role = Literal["client", "trusted", "operator", "demo"]
TransferStatus = Literal["ASSESSING", "PAUSED", "HELD", "COMPLETED", "REJECTED", "CANCELLED"]
RiskLevel = Literal["low", "medium", "high"]
SignalStatus = Literal["ready", "pending", "unknown"]
SignalSource = Literal["llm", "dictionary", "none"]
Scheme = Literal["bank_security", "relative_in_trouble", "investment", "marketplace", "none"]
ApprovalPolicy = Literal["trusted_allowed", "operator_required"]
ApprovalStatus = Literal["PENDING", "APPROVED", "REJECTED", "EXPIRED", "CANCELLED"]
AlertPriority = Literal["medium", "high"]
AlertKind = Literal["fraud_suspected", "approval_expired", "assessment_interrupted"]
AlertStatus = Literal["OPEN", "RESOLVED"]
AlertAction = Literal["release", "reject", "mark_fraud"]
TransferAction = Literal["answer", "cancel"]
SpeechState = Literal["idle", "recording", "recognizing", "error"]
PhraseFeature = Literal["urgency", "secrecy", "safe_account", "impersonation"]
PhraseContext = Literal["request", "warning", "quotation"]
QuestionId = Literal["recipient_known", "request_context"]
AnswerValue = Literal["yes", "no", "unsure"]
ReasonCode = Literal[
    "new_recipient", "unusual_amount", "active_urgent_request", "secrecy_request",
    "safe_account_request", "call_reported", "remote_access_simulated",
    "strong_active_request", "speech_pending", "speech_unknown",
    "dictionary_uncertain", "approval_expired", "assessment_interrupted",
]
ErrorCode = Literal[
    "invalid_request", "invalid_amount", "invalid_pin", "insufficient_funds",
    "unauthorized", "forbidden", "not_found", "method_not_allowed",
    "idempotency_conflict", "revision_conflict", "invalid_transition",
    "approval_expired", "dialogue_ended", "segment_conflict", "demo_disabled",
    "stt_unavailable", "audio_invalid", "audio_too_large", "internal_error",
]
EntityId = Annotated[str, StringConstraints(min_length=1, max_length=128)]
Money = Annotated[int, Field(strict=True, gt=0, le=9007199254740991)]
Balance = Annotated[int, Field(strict=True, ge=0, le=9007199254740991)]
Revision = Annotated[int, Field(strict=True, ge=1, le=9007199254740991)]
Sequence = Annotated[int, Field(strict=True, ge=1, le=9007199254740991)]
Evidence = Annotated[str, StringConstraints(min_length=1, max_length=120)]


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=False)

    @field_serializer("*", when_used="json", check_fields=False)
    def serialize_datetime(self, value):
        # Every wire timestamp is timezone-aware and serialized in UTC.
        from datetime import UTC, datetime
        if isinstance(value, datetime):
            return value.astimezone(UTC).isoformat().replace("+00:00", "Z")
        return value


class ClassifierResult(Contract):
    # Preserve this declaration order: architecture 4.2 / M02.
    scheme: Scheme
    active_request: bool = Field(strict=True)
    urgency: bool = Field(strict=True)
    secrecy: bool = Field(strict=True)
    safe_account_request: bool = Field(strict=True)
    evidence: list[Evidence] = Field(max_length=3)


class SpeechAssessment(ClassifierResult):
    status: SignalStatus
    source: SignalSource
    model: str | None
    session_id: EntityId | None
    segment_seq: Annotated[int, Field(strict=True, ge=0, le=9007199254740991)]
    received_at: AwareDatetime
    uncertain: bool

    @model_validator(mode="after")
    def source_consistency(self) -> "SpeechAssessment":
        if self.source == "llm" and (not self.model or self.status != "ready"):
            raise ValueError("An LLM result must identify the responding model and be ready")
        if self.source != "llm" and self.model is not None:
            raise ValueError("Only LLM results have a model")
        if (self.source == "none") != (self.status in {"unknown", "pending"}):
            raise ValueError("Missing/pending assessment must have source=none")
        if self.source == "none" and (
            self.scheme != "none" or self.active_request or self.urgency
            or self.secrecy or self.safe_account_request or self.evidence
        ):
            raise ValueError("Missing assessment cannot contain inferred features")
        return self


class Reason(Contract):
    code: ReasonCode
    text: str = Field(min_length=1, max_length=500)
    evidence: Evidence | None = None


class PauseQuestion(Contract):
    id: QuestionId
    text: str = Field(min_length=1, max_length=500)


class RiskView(Contract):
    level: RiskLevel
    score: Annotated[int, Field(strict=True, ge=0, le=100)]
    policy: ApprovalPolicy
    reasons: list[Reason]
    speech: SpeechAssessment
    questions: list[PauseQuestion]


class RecipientView(Contract):
    id: EntityId
    label: str = Field(min_length=1, max_length=200)
    is_new: bool


class CustomerView(Contract):
    id: EntityId
    label: str
    balance_tenge: Balance
    reserved_tenge: Balance
    available_tenge: Balance


class TransferView(Contract):
    id: EntityId
    revision: Revision
    amount_tenge: Money
    recipient_id: EntityId
    recipient_label: str
    status: TransferStatus
    risk: RiskView
    allowed_actions: list[TransferAction]
    created_at: AwareDatetime
    updated_at: AwareDatetime


class ApprovalView(Contract):
    id: EntityId
    revision: Revision
    transfer_id: EntityId
    transfer_revision: Revision
    amount_tenge: Money
    recipient_id: EntityId
    recipient_label: str
    status: ApprovalStatus
    policy: ApprovalPolicy
    expires_at: AwareDatetime
    can_respond: bool


class AlertView(Contract):
    id: EntityId
    revision: Revision
    transfer_id: EntityId
    transfer_revision: Revision
    amount_tenge: Money
    recipient_label: str
    priority: AlertPriority
    kind: AlertKind
    reasons: list[Reason]
    status: AlertStatus
    allowed_actions: list[AlertAction]
    created_at: AwareDatetime


class ErrorResponse(Contract):
    code: ErrorCode
    message: str
    request_id: str


class LlmHealth(Contract):
    available: bool
    model: str | None


class SttHealth(Contract):
    available: bool


class HealthResponse(Contract):
    status: Literal["ok"] = "ok"
    llm: LlmHealth
    stt: SttHealth


class CreateDialogueRequest(Contract):
    language: DialogueLanguage


class DialogueView(Contract):
    id: EntityId
    language: DialogueLanguage
    status: Literal["active", "ended"]
    last_seq: Annotated[int, Field(strict=True, ge=0, le=9007199254740991)]
    speech: SpeechAssessment


class AddSegmentRequest(Contract):
    seq: Sequence
    speaker: Speaker
    text: str = Field(min_length=1, max_length=6000)


class SegmentResponse(Contract):
    session_id: EntityId
    seq: Sequence
    accepted: bool
    speech: SpeechAssessment


class EndDialogueRequest(Contract):
    pass


class CreateTransferRequest(Contract):
    amount_tenge: Money
    recipient_id: EntityId
    pin: str = Field(pattern=r"^[0-9]{4,6}$", repr=False, exclude=False)
    language: Language
    dialogue_id: EntityId | None = None


class PauseAnswer(Contract):
    question_id: QuestionId
    value: AnswerValue


class AnswerPauseRequest(Contract):
    expected_revision: Revision
    answers: list[PauseAnswer] = Field(min_length=1, max_length=2)

    @model_validator(mode="after")
    def unique_questions(self) -> "AnswerPauseRequest":
        ids = [answer.question_id for answer in self.answers]
        if len(ids) != len(set(ids)):
            raise ValueError("Question IDs must be unique")
        return self


class CancelTransferRequest(Contract):
    expected_revision: Revision


class RespondApprovalRequest(Contract):
    expected_revision: Revision
    approve: bool = Field(strict=True)


class ResolveAlertRequest(Contract):
    expected_revision: Revision
    action: AlertAction
    note: str = Field(min_length=1, max_length=500)


class DemoSignals(Contract):
    call_reported: bool = Field(strict=True)
    remote_access: bool = Field(strict=True)
    source: Literal["simulated"] = "simulated"


class DemoScriptView(Contract):
    id: Literal["ru-fraud", "ru-normal", "kk-fraud", "kk-normal", "mixed-fraud", "mixed-normal"]
    language: DialogueLanguage
    intended_case: str


class ResetDemoRequest(Contract):
    pass


class ResetDemoResponse(Contract):
    reset: Literal[True] = True
    snapshot_id: EntityId


class ReplayDemoRequest(Contract):
    pass


class ReplayDemoResponse(Contract):
    script_id: str
    dialogue_id: EntityId
    status: Literal["started"] = "started"


class AudioTranscriptionResponse(Contract):
    seq: Sequence
    text: str
    language: Language


class SnapshotBase(Contract):
    snapshot_id: EntityId
    server_time: AwareDatetime
    language: Language


class ClientSnapshot(SnapshotBase):
    role: Literal["client"]
    customer: CustomerView
    recipients: list[RecipientView]
    transfers: list[TransferView]
    dialogue: DialogueView | None


class TrustedSnapshot(SnapshotBase):
    role: Literal["trusted"]
    approvals: list[ApprovalView]


class OperatorSnapshot(SnapshotBase):
    role: Literal["operator"]
    alerts: list[AlertView]


class DemoSnapshot(SnapshotBase):
    role: Literal["demo"]
    signals: DemoSignals
    scripts: list[DemoScriptView]
    active_dialogue_id: EntityId | None


Snapshot = Annotated[
    ClientSnapshot | TrustedSnapshot | OperatorSnapshot | DemoSnapshot,
    Field(discriminator="role"),
]


class SnapshotChangedEvent(Contract):
    type: Literal["snapshot_changed"]
    snapshot_id: EntityId
    occurred_at: AwareDatetime


class PhraseEntry(Contract):
    id: Annotated[str, StringConstraints(pattern=r"^(ru|kk)-00[1-9]$|^(ru|kk)-01[0-6]$")]
    language: Language
    scheme: Scheme
    phrase: str = Field(min_length=1, max_length=120)
    feature: PhraseFeature
    context: PhraseContext

    @model_validator(mode="after")
    def id_language(self) -> "PhraseEntry":
        if not self.id.startswith(self.language + "-"):
            raise ValueError("Phrase ID must match language")
        return self


class DemoSegment(Contract):
    seq: Sequence
    speaker: Literal["caller", "customer"]
    text: str = Field(min_length=1, max_length=6000)
    delay_ms: Annotated[int, Field(strict=True, ge=500, le=1500)]


class DemoDialogue(Contract):
    id: Literal["ru-fraud", "ru-normal", "kk-fraud", "kk-normal", "mixed-fraud", "mixed-normal"]
    language: DialogueLanguage
    synthetic: Literal[True]
    intended_case: str = Field(min_length=1, max_length=500)
    segments: list[DemoSegment] = Field(min_length=4, max_length=8)

    @model_validator(mode="after")
    def segment_order(self) -> "DemoDialogue":
        if not self.id.startswith(self.language + "-"):
            raise ValueError("Script ID must match language")
        if [segment.seq for segment in self.segments] != list(range(1, len(self.segments) + 1)):
            raise ValueError("Demo segments must be numbered consecutively from 1")
        return self
