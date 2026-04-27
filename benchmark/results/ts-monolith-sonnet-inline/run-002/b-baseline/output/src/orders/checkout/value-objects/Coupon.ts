import { Money } from '../../../shared/value-objects/Money';

/** Discount coupon applicable during checkout. */
export interface Coupon {
  code: string;
  discount: Money;
}
