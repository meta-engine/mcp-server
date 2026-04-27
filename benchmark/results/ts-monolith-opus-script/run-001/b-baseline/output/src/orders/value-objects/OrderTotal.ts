import { Money } from '../../shared/value-objects/Money';

/** OrderTotal value object aggregating subtotal, tax and grand total. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
