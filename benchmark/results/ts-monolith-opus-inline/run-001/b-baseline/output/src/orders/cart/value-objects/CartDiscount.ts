import { Money } from "../../../shared/value-objects/Money";

/** A discount applied to a shopping cart. */
export interface CartDiscount {
  code: string;
  amount: Money;
}
