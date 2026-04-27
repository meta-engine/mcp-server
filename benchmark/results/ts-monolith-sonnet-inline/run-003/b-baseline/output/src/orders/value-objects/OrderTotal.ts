import { Money } from '../../shared/value-objects/Money';

/** Breakdown of monetary totals for an order. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
