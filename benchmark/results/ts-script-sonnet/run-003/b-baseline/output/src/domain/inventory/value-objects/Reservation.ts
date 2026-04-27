/** Value object representing a stock reservation for a pending order. */
export interface Reservation {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
