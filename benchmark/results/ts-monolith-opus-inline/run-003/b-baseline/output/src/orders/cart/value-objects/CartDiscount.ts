import { Money } from "../../../shared/value-objects/Money";

/** Discount applied to a Cart. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
