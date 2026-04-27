import { Money } from '../../shared/value-objects/money';

/** InvoiceLine value object. */
export interface InvoiceLine {
  description: string;
  amount: Money;
}
