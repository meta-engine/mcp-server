import { Money } from '../../../shared/value-objects/Money';

/** Discount coupon with a code and monetary value. */
export interface Coupon {
  code: string;
  discount: Money;
}
