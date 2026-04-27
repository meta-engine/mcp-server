import { Money } from '../../shared/value-objects/Money';

/** TaxLine value object describing a tax component on an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
