import { Money } from '../../shared/value-objects/Money';

/** Tax line entry on an invoice with rate and computed amount. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
