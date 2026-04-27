import { Money } from '../../shared/value-objects/Money';

/** OrderTotal value object */
export interface OrderTotal {
  readonly subtotal: Money;
  readonly tax: Money;
  readonly grandTotal: Money;
}
