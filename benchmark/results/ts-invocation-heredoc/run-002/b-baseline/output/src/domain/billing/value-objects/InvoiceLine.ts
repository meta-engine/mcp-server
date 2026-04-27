/** Line item value object for an invoice. */
export interface InvoiceLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
