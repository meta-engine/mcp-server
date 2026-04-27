/** Value object representing a grouping dimension for analytics data. */
export interface Dimension {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
