/** Metric value object representing a quantitative measurement in analytics. */
export interface Metric {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
