/** Value object representing a quantitative metric derived from analytics events. */
export interface Metric {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
