import { Money } from '../../../shared/value-objects/Money';

/** Discount coupon redeemable at checkout */
export interface Coupon {
  code: string;
  discount: Money;
}
