/** Value object representing payment terms for an invoice. */
export interface PaymentTerms {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
