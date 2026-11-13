/** Handwritten wire types matching backend/app/schemas.py. No client scoring. */
export type Language = "ru" | "kk";
export type DialogueLanguage = Language | "mixed";
export type Speaker = "caller" | "customer" | "unknown";
export type Role = "client" | "trusted" | "operator" | "demo";
export type TransferStatus = "ASSESSING" | "PAUSED" | "HELD" | "COMPLETED" | "REJECTED" | "CANCELLED";
export type RiskLevel = "low" | "medium" | "high";
export type SignalStatus = "ready" | "pending" | "unknown";
export type SignalSource = "llm" | "dictionary" | "none";
export type Scheme = "bank_security" | "relative_in_trouble" | "investment" | "marketplace" | "none";
export type ApprovalPolicy = "trusted_allowed" | "operator_required";
export type ApprovalStatus = "PENDING" | "APPROVED" | "REJECTED" | "EXPIRED" | "CANCELLED";
export type AlertPriority = "medium" | "high";
export type AlertKind = "fraud_suspected" | "approval_expired" | "assessment_interrupted";
export type AlertStatus = "OPEN" | "RESOLVED";
export type AlertAction = "release" | "reject" | "mark_fraud";
export type TransferAction = "answer" | "cancel";
export type SpeechState = "idle" | "recording" | "recognizing" | "error";
export type AudioLanguage = Language | "auto";
export type PhraseFeature = "urgency" | "secrecy" | "safe_account" | "impersonation";
export type PhraseContext = "request" | "warning" | "quotation";
export type QuestionId = "recipient_known" | "request_context";
export type AnswerValue = "yes" | "no" | "unsure";
export type ReasonCode =
  | "new_recipient" | "unusual_amount" | "active_urgent_request" | "secrecy_request"
  | "safe_account_request" | "call_reported" | "remote_access_simulated"
  | "strong_active_request" | "speech_pending" | "speech_unknown"
  | "dictionary_uncertain" | "approval_expired" | "assessment_interrupted";
export type ErrorCode =
  | "invalid_request" | "invalid_amount" | "invalid_pin" | "insufficient_funds"
  | "unauthorized" | "forbidden" | "not_found" | "method_not_allowed"
  | "idempotency_conflict" | "revision_conflict" | "invalid_transition"
  | "approval_expired" | "dialogue_ended" | "segment_conflict" | "demo_disabled"
  | "stt_unavailable" | "audio_invalid" | "audio_too_large" | "internal_error";

/** IDs are opaque; UTC strings end in Z. Integers are safe JS integers. */
export type EntityId = string;
export type UtcTimestamp = string;
export type Money = number;
export type Balance = number;
export type Revision = number;
export type Sequence = number;
export type Evidence = string;

export interface ClassifierResult {
  scheme: Scheme;
  active_request: boolean;
  urgency: boolean;
  secrecy: boolean;
  safe_account_request: boolean;
  evidence: Evidence[];
}
export interface SpeechAssessment extends ClassifierResult {
  status: SignalStatus;
  source: SignalSource;
  model: string | null;
  session_id: EntityId | null;
  segment_seq: number;
  received_at: UtcTimestamp;
  uncertain: boolean;
}
export interface Reason { code: ReasonCode; text: string; evidence?: Evidence | null }
export interface PauseQuestion { id: QuestionId; text: string }
export interface RiskView {
  level: RiskLevel;
  score: number;
  policy: ApprovalPolicy;
  reasons: Reason[];
  speech: SpeechAssessment;
  questions: PauseQuestion[];
}
export interface RecipientView { id: EntityId; label: string; is_new: boolean }
export interface CustomerView {
  id: EntityId;
  label: string;
  balance_tenge: Balance;
  reserved_tenge: Balance;
  available_tenge: Balance;
}
export interface TransferView {
  id: EntityId;
  revision: Revision;
  amount_tenge: Money;
  recipient_id: EntityId;
  recipient_label: string;
  status: TransferStatus;
  risk: RiskView;
  allowed_actions: TransferAction[];
  created_at: UtcTimestamp;
  updated_at: UtcTimestamp;
}
export interface ApprovalView {
  id: EntityId;
  revision: Revision;
  transfer_id: EntityId;
  transfer_revision: Revision;
  amount_tenge: Money;
  recipient_id: EntityId;
  recipient_label: string;
  status: ApprovalStatus;
  policy: ApprovalPolicy;
  expires_at: UtcTimestamp;
  can_respond: boolean;
}
export interface AlertView {
  id: EntityId;
  revision: Revision;
  transfer_id: EntityId;
  transfer_revision: Revision;
  amount_tenge: Money;
  recipient_label: string;
  priority: AlertPriority;
  kind: AlertKind;
  reasons: Reason[];
  status: AlertStatus;
  allowed_actions: AlertAction[];
  created_at: UtcTimestamp;
}
export interface ErrorResponse { code: ErrorCode; message: string; request_id: string }
export interface LlmHealth { available: boolean; model: string | null }
export interface SttHealth { available: boolean }
export interface HealthResponse { status: "ok"; llm: LlmHealth; stt: SttHealth }
export interface CreateDialogueRequest { language: DialogueLanguage }
export interface DialogueView {
  id: EntityId;
  language: DialogueLanguage;
  status: "active" | "ended";
  last_seq: number;
  speech: SpeechAssessment;
}
export interface AddSegmentRequest { seq: Sequence; speaker: Speaker; text: string }
export interface SegmentResponse {
  session_id: EntityId;
  seq: Sequence;
  accepted: boolean;
  speech: SpeechAssessment;
}
export type EndDialogueRequest = Record<string, never>;
export interface CreateTransferRequest {
  amount_tenge: Money;
  recipient_id: EntityId;
  pin: string;
  language: Language;
  dialogue_id?: EntityId | null;
}
export interface PauseAnswer { question_id: QuestionId; value: AnswerValue }
export interface AnswerPauseRequest { expected_revision: Revision; answers: PauseAnswer[] }
export interface CancelTransferRequest { expected_revision: Revision }
export interface RespondApprovalRequest { expected_revision: Revision; approve: boolean }
export interface ResolveAlertRequest { expected_revision: Revision; action: AlertAction; note: string }
export interface DemoSignals { call_reported: boolean; remote_access: boolean; source: "simulated" }
export type DemoScriptId = "ru-fraud" | "ru-normal" | "kk-fraud" | "kk-normal" | "mixed-fraud" | "mixed-normal";
export interface DemoScriptView { id: DemoScriptId; language: DialogueLanguage; intended_case: string }
export type ResetDemoRequest = Record<string, never>;
export interface ResetDemoResponse { reset: true; snapshot_id: EntityId }
export type ReplayDemoRequest = Record<string, never>;
export interface ReplayDemoResponse { script_id: string; dialogue_id: EntityId; status: "started" }
export interface AudioTranscriptionResponse { seq: Sequence; text: string; language: Language }
export interface SnapshotBase { snapshot_id: EntityId; server_time: UtcTimestamp; language: Language }
export interface ClientSnapshot extends SnapshotBase {
  role: "client";
  customer: CustomerView;
  recipients: RecipientView[];
  transfers: TransferView[];
  dialogue: DialogueView | null;
}
export interface TrustedSnapshot extends SnapshotBase { role: "trusted"; approvals: ApprovalView[] }
export interface OperatorSnapshot extends SnapshotBase { role: "operator"; alerts: AlertView[] }
export interface DemoSnapshot extends SnapshotBase {
  role: "demo";
  signals: DemoSignals;
  scripts: DemoScriptView[];
  active_dialogue_id: EntityId | null;
}
export type Snapshot = ClientSnapshot | TrustedSnapshot | OperatorSnapshot | DemoSnapshot;
export interface SnapshotChangedEvent {
  type: "snapshot_changed";
  snapshot_id: EntityId;
  occurred_at: UtcTimestamp;
}
export interface PhraseEntry {
  id: string;
  language: Language;
  scheme: Scheme;
  phrase: string;
  feature: PhraseFeature;
  context: PhraseContext;
}
export interface DemoSegment { seq: Sequence; speaker: "caller" | "customer"; text: string; delay_ms: number }
export interface DemoDialogue {
  id: DemoScriptId;
  language: DialogueLanguage;
  synthetic: true;
  intended_case: string;
  segments: DemoSegment[];
}
