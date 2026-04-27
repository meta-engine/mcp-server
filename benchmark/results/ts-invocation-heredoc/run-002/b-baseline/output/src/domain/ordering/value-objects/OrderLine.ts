/** Line item value object for an order. */
export interface OrderLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
