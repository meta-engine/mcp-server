/** Value object representing a quantitative analytics metric. */
export interface Metric {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
