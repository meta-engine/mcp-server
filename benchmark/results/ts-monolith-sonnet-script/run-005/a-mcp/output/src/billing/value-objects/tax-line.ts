import { Money } from '../../shared/value-objects/money';

export interface TaxLine {
  rate: number;
  amount: Money;
}
