/** Permission value object. */
export interface Permission {
  readonly id: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly name: string;
  readonly description: string;
}
