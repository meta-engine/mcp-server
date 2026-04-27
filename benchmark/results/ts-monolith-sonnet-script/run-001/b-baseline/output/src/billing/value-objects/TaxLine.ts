import { Money } from '../../shared/value-objects/Money';

/** A tax entry on an invoice with rate and computed amount. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
