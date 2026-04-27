import { Money } from '../../shared/value-objects/Money';

/** A single line item on a billing invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
