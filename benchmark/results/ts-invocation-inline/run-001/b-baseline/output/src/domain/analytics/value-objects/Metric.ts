/** Value object representing a measured metric. */
export interface Metric {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
