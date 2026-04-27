/** Value object representing a single line in an order. */
export interface OrderLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
