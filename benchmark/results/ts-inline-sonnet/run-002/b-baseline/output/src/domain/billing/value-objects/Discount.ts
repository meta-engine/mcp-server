/** Value object representing a discount applied to a billing item. */
export interface Discount {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
