/** Value object representing an applied tax line on an invoice. */
export interface TaxLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
