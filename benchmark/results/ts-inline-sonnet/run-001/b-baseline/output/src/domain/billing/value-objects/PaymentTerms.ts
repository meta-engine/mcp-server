/** PaymentTerms value object representing the agreed payment conditions for an invoice. */
export interface PaymentTerms {
  id: string;
  createdAt: Date;
  updatedAt: Date;
  name: string;
  description: string;
}
