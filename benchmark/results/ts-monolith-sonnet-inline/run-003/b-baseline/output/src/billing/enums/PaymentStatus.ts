/** State of a payment transaction. */
export enum PaymentStatus {
  Pending = 0,
  Succeeded = 1,
  Failed = 2,
  Refunded = 3,
}
