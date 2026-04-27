/** Reservation value object. */
export interface Reservation {
  readonly id: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly name: string;
  readonly description: string;
}
