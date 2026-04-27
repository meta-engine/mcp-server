import { Money } from '../../../shared/value-objects/Money';

/** Discount applied to a cart via a promo code. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
