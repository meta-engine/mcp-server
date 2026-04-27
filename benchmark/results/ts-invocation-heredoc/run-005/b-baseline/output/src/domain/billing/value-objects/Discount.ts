/** Value object representing a discount applied to an invoice. */
export interface Discount {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
