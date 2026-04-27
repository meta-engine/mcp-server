/** Value object capturing a product's descriptive metadata. */
export interface ProductDescription {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
