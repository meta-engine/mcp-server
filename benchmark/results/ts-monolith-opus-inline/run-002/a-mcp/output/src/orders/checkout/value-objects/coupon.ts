import { Money } from '../../../shared/value-objects/money';

/** Coupon value object. */
export interface Coupon {
  code: string;
  discount: Money;
}
