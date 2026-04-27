import { Money } from '../../shared/value-objects/Money';

/** Represents a line item on an invoice. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
