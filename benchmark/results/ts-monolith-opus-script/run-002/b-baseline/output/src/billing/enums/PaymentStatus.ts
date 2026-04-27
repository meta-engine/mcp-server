/** Outcome state of a payment attempt. */
export enum PaymentStatus {
  Pending = 0,
  Succeeded = 1,
  Failed = 2,
  Refunded = 3,
}
