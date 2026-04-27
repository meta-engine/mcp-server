/** Value object representing a product category in the catalog. */
export interface Category {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
