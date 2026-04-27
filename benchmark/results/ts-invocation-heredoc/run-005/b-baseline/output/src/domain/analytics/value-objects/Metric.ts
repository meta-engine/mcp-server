/** Value object representing an analytics metric. */
export interface Metric {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
