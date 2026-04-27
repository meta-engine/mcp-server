import { Money } from '../../../shared/value-objects/Money';

/** Promotional coupon with a discount amount. */
export interface Coupon {
  code: string;
  discount: Money;
}
