import { Money } from '../../../shared/value-objects/money';

/** CartDiscount value object. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
