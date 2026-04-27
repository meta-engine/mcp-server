import { Money } from "../../../shared/value-objects/Money";

/** Coupon value object. */
export interface Coupon {
  code: string;
  discount: Money;
}
