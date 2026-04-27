/** Value object holding descriptive metadata about a product. */
export interface ProductDescription {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
