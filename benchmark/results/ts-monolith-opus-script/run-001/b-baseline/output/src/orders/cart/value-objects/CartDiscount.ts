import { Money } from '../../../shared/value-objects/Money';

/** CartDiscount value object describing a discount applied to a cart. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
