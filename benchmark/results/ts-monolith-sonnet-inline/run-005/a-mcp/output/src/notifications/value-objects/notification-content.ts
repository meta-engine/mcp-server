import { NotificationKind } from '../enums/notification-kind.enum';

/** NotificationContent value object. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
