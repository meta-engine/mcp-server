import { NotificationKind } from '../enums/NotificationKind';

/** Notification payload with channel kind. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
