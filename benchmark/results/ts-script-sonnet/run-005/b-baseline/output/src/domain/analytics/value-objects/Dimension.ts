/** Value object representing a segmentation dimension for analytics queries. */
export interface Dimension {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
