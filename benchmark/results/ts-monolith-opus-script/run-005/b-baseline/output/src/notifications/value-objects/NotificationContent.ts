import { NotificationKind } from "../enums/NotificationKind";

/** Channel-typed notification payload. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
