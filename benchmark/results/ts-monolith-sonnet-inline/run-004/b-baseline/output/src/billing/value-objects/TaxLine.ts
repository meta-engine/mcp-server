import { Money } from '../../shared/value-objects/Money';

/** Tax component applied on a billing document */
export interface TaxLine {
  rate: number;
  amount: Money;
}
