import { Money } from '../../shared/value-objects/Money';

/** Tax applied at a specific rate on an invoice. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
