import { Money } from '../../shared/value-objects/Money';

/** InvoiceLine value object representing a line item on an invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
