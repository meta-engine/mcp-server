/** OrderLine value object. */
export interface OrderLine {
  readonly id: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly name: string;
  readonly description: string;
}
