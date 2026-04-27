import { Money } from '../../shared/value-objects/Money';

/** TaxLine value object representing a tax line on a billing document. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
