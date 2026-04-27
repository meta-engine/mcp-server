import { Money } from "../../../shared/value-objects/Money";

/** Discount applied to a cart. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
