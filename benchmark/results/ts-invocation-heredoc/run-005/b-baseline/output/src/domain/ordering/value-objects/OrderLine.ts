/** Value object representing a line on an order. */
export interface OrderLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
