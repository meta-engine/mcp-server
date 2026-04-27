import { NotificationKind } from '../enums/NotificationKind';

/** NotificationContent value object representing notification payload and kind. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
