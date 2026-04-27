import { Money } from "../../../shared/value-objects/Money";

/** Discount coupon applicable at checkout. */
export interface Coupon {
  code: string;
  discount: Money;
}
