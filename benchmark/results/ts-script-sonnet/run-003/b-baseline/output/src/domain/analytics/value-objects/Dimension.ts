/** Value object representing a categorical dimension used to slice analytics data. */
export interface Dimension {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
