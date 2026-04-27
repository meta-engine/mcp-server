import { Money } from '../../../shared/value-objects/Money';

/** Represents a discount coupon applied during checkout. */
export interface Coupon {
  code: string;
  discount: Money;
}
