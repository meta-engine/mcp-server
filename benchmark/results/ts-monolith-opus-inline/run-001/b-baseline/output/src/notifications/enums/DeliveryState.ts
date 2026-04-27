/** Lifecycle state of a delivery attempt. */
export enum DeliveryState {
  Queued = 0,
  Sent = 1,
  Delivered = 2,
  Failed = 3,
}
