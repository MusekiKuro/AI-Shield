import type {
  AlertAction, AlertKind, AlertPriority, AlertStatus, AlertView, ApprovalStatus,
  ApprovalView, Language, Reason, RecipientView, RiskLevel, SpeechState,
} from "../api/types";

export interface TransferFormLabels {
  title: string;
  recipient: string;
  recipientPlaceholder: string;
  amount: string;
  amountHint: string;
  pin: string;
  pinHint: string;
  submit: string;
  submitting: string;
}
export interface TransferFormProps {
  recipients: readonly RecipientView[];
  amountText: string;
  recipientId: string;
  pin: string;
  busy: boolean;
  error: string | null;
  labels: TransferFormLabels;
  onAmountChange: (value: string) => void;
  onRecipientChange: (value: string) => void;
  onPinChange: (value: string) => void;
  onSubmit: () => void;
}

export interface RiskNoticeProps {
  level: RiskLevel;
  levelLabel: string;
  reasons: readonly Reason[];
  sourceLabel: string;
  dataStatusLabel: string;
  title: string;
  scoreLabel?: string;
  emptyReasonsLabel: string;
  evidenceLabel: string;
}

export interface ApprovalCardLabels {
  title: string;
  amount: string;
  recipient: string;
  question: string;
  expiresAt: string;
  approve: string;
  reject: string;
  responding: string;
  status: Record<ApprovalStatus, string>;
  operatorRequired: string;
}
export interface ApprovalCardProps {
  approval: ApprovalView;
  language: Language;
  busy: boolean;
  error: string | null;
  labels: ApprovalCardLabels;
  onRespond: (approvalId: string, approve: boolean) => void;
}

export interface AlertCardLabels {
  title: string;
  transferId: string;
  amount: string;
  recipient: string;
  priority: Record<AlertPriority, string>;
  kind: Record<AlertKind, string>;
  status: Record<AlertStatus, string>;
  actions: Record<AlertAction, string>;
  note: string;
  noteHint: string;
  noActions: string;
  resolving: string;
  reasons: string;
  emptyReasons: string;
  evidence: string;
}
export interface AlertCardProps {
  alert: AlertView;
  language: Language;
  labels: AlertCardLabels;
  busy: boolean;
  error: string | null;
  onResolve: (alertId: string, action: AlertAction, note: string) => void;
}

export interface SpeechControlsLabels {
  title: string;
  consent: string;
  privacy: string;
  start: string;
  stop: string;
  partialText: string;
  finalText: string;
  state: Record<SpeechState, string>;
}
/** F12 contract is fixed in C01; C06 supplies consent and recording behavior. */
export interface SpeechControlsProps {
  consent: boolean;
  state: SpeechState;
  partialText: string;
  finalText: string;
  error: string | null;
  labels: SpeechControlsLabels;
  onConsentChange: (value: boolean) => void;
  onStart: () => void;
  onStop: () => void;
}
