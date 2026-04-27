import { Money } from '../../shared/value-objects/money';

/** TaxLine value object. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
