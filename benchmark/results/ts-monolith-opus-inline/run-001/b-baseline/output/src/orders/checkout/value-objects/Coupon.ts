import { Money } from "../../../shared/value-objects/Money";

/** A coupon applicable at checkout. */
export interface Coupon {
  code: string;
  discount: Money;
}
