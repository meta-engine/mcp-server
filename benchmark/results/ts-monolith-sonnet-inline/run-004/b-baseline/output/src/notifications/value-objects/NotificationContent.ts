import { NotificationKind } from '../enums/NotificationKind';

/** Content payload for a notification dispatch */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
