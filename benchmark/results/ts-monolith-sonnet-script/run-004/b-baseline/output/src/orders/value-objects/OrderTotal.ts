import { Money } from '../../shared/value-objects/Money';

/** OrderTotal value object representing order cost breakdown. */
export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
