import { Money } from "../../../shared/value-objects/Money";

/** Discount coupon usable at checkout. */
export interface Coupon {
  code: string;
  discount: Money;
}
