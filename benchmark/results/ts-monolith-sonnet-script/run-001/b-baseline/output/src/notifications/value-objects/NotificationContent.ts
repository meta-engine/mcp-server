import { NotificationKind } from '../enums/NotificationKind';

/** Notification payload and its delivery channel. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
