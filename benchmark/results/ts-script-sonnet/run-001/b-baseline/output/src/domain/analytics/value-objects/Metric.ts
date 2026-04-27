/** Metric value object. */
export interface Metric {
  readonly id: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly name: string;
  readonly description: string;
}
