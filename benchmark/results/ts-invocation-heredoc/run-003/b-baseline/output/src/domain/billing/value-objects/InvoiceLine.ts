/** Value object representing an invoice line. */
export interface InvoiceLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
