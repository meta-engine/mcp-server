import { NotificationKind } from '../enums/NotificationKind';

/** NotificationContent value object describing notification kind and payload. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
