import { Money } from '../../../shared/value-objects/Money';

/** A discount applied to a cart via a promo code. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
