/** InvoiceLine value object. */
export interface InvoiceLine {
  readonly id: string;
  readonly createdAt: Date;
  readonly updatedAt: Date;
  readonly name: string;
  readonly description: string;
}
