/** Value object representing a single line item within an order. */
export interface OrderLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
