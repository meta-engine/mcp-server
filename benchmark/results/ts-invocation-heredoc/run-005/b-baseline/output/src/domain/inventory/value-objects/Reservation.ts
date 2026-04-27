/** Value object describing a stock reservation. */
export interface Reservation {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
