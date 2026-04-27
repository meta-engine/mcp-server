import { NotificationKind } from '../enums/NotificationKind';

/** Content payload for a notification delivery. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
