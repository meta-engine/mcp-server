import { Money } from '../../shared/value-objects/Money';

/** Computed totals for an order. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
