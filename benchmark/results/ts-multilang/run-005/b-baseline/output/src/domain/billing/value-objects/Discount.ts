/** Value object representing a discount on an invoice. */
export interface Discount {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
