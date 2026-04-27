/** Value object describing payment terms on an invoice. */
export interface PaymentTerms {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
