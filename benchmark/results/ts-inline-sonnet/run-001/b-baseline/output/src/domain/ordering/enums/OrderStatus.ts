/** OrderStatus enum representing the lifecycle states of an order. */
export enum OrderStatus {
  Draft = 0,
  Placed = 1,
  Paid = 2,
  Shipped = 3,
  Delivered = 4,
  Cancelled = 5,
}
