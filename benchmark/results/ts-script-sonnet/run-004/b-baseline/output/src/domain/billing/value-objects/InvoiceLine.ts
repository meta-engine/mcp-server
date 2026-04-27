/** Value object representing a single line on an invoice. */
export interface InvoiceLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
