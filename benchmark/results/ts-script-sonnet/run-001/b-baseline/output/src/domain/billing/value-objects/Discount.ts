/** Discount value object. */
export interface Discount {
  readonly id: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly name: string;
  readonly description: string;
}
