import { NotificationKind } from "../enums/NotificationKind";

/** Channel-tagged payload to deliver to a recipient. */
export interface NotificationContent {
  kind: NotificationKind;
  payload: string;
}
