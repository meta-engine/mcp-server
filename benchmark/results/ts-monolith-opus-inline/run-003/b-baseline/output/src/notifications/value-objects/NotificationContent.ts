import { NotificationKind } from "../enums/NotificationKind";

/** Channel-specific notification payload. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
