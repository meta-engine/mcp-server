/** Value object representing a line on an invoice. */
export interface InvoiceLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
