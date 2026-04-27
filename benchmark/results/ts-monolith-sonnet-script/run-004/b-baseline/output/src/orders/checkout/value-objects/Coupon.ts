import { Money } from '../../../shared/value-objects/Money';

/** Coupon value object representing a discount coupon. */
export interface Coupon {
  code: string;
  discount: Money;
}
