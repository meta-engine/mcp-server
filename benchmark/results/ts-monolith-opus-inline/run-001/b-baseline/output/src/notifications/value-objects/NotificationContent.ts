import { NotificationKind } from "../enums/NotificationKind";

/** Concrete payload for a notification of a specific kind. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
