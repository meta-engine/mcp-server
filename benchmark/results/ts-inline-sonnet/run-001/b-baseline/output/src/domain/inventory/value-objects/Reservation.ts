/** Reservation value object representing a hold placed on inventory stock. */
export interface Reservation {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
