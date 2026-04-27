/** Value object representing the payment terms agreed for an invoice. */
export interface PaymentTerms {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
