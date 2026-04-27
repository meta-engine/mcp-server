import { Money } from '../../shared/value-objects/Money';

/** Tax line entry on an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
