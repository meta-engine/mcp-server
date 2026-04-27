import { Money } from '../../shared/value-objects/Money';

/** TaxLine value object */
export interface TaxLine {
  readonly rate: number;
  readonly amount: Money;
}
