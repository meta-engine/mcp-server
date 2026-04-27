import { NotificationKind } from '../enums/NotificationKind';

/** Notification content with channel kind and serialized payload. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
