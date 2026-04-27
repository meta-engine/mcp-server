/** Value object representing an order line. */
export interface OrderLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
