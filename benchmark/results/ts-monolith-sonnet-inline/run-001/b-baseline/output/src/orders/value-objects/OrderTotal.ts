import { Money } from '../../shared/value-objects/Money';

/** Represents the computed totals for an order. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
