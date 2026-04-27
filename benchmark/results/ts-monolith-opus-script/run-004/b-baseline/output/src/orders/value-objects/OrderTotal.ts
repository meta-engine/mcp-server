import { Money } from "../../shared/value-objects/Money";

/** OrderTotal value object. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
