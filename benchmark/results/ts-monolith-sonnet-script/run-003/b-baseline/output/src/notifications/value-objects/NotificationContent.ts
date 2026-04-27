import { NotificationKind } from '../enums/NotificationKind';

/** NotificationContent value object */
export interface NotificationContent {
  readonly kind: NotificationKind;
  readonly payload: string;
}
