import { Money } from '../../shared/value-objects/money';

/** OrderTotal value object. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
