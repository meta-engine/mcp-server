import { Money } from '../../shared/value-objects/Money';

/** Single line item on an invoice */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
