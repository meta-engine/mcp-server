import { NotificationKind } from '../enums/notification-kind.enum';

export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
