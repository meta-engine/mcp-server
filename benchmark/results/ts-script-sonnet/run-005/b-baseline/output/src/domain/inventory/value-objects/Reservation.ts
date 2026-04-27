/** Value object representing a stock reservation held for an order. */
export interface Reservation {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
