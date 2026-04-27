import { Money } from '../../shared/value-objects/Money';

/** InvoiceLine value object describing a single line item on an invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
