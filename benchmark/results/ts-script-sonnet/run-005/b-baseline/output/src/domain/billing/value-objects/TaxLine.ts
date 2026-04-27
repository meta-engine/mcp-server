/** Value object representing a tax line entry on an invoice. */
export interface TaxLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
