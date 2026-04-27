import { Money } from '../../shared/value-objects/Money';

/** Represents a tax line on a billing document. */
export interface TaxLine {
  rate: number;
  amount: Money;
}
