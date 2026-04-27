import { NotificationKind } from '../enums/NotificationKind';

/** Notification content with its channel kind and serialised payload. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
