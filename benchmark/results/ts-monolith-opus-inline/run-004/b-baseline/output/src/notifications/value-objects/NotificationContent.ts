import { NotificationKind } from '../enums/NotificationKind';

/** NotificationContent value object. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
