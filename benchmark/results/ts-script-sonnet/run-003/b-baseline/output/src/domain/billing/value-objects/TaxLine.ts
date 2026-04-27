/** Value object representing a tax charge line on an invoice. */
export interface TaxLine {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
