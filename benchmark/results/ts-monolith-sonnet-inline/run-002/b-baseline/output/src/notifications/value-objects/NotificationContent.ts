import { NotificationKind } from '../enums/NotificationKind';

/** Payload and channel descriptor for a notification. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
