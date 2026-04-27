/** Discount value object representing a price reduction applied to an invoice. */
export interface Discount {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
