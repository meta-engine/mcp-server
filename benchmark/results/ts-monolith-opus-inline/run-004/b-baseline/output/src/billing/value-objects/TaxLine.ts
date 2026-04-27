import { Money } from '../../shared/value-objects/Money';

/** TaxLine value object. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
