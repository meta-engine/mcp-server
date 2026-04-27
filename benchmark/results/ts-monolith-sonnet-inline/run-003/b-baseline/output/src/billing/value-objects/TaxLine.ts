import { Money } from '../../shared/value-objects/Money';

/** Tax component on an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
