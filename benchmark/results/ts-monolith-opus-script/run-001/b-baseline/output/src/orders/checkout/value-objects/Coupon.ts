import { Money } from '../../../shared/value-objects/Money';

/** Coupon value object describing a discount code and its monetary value. */
export interface Coupon {
  code: string;
  discount: Money;
}
