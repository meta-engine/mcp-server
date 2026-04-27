import { Money } from '../../shared/value-objects/money';

export interface OrderTotal {
  subtotal: Money;
  tax: Money;
  grandTotal: Money;
}
