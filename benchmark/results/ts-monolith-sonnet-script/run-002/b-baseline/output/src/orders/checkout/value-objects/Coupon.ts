import { Money } from '../../../shared/value-objects/Money';

/** Discount coupon redeemable during checkout. */
export interface Coupon {
  code: string;
  discount: Money;
}
