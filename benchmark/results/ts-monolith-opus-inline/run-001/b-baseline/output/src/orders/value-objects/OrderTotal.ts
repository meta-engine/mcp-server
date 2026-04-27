import { Money } from "../../shared/value-objects/Money";

/** Breakdown of an order's monetary total. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
