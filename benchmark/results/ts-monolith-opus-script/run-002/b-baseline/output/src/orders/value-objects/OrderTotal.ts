import { Money } from "../../shared/value-objects/Money";

/** Subtotal, tax, and grand total for an order. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
