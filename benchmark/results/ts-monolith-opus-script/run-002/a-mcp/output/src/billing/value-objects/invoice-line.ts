import { Money } from '../../shared/value-objects/money';

export interface InvoiceLine {
  description: string;
  amount: Money;
}
