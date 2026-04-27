import { NotificationKind } from '../enums/NotificationKind';

/** Represents the content of a notification. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
