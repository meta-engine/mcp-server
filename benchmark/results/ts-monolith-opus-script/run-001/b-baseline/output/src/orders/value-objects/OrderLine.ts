import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';

/** OrderLine value object describing a single line on an order. */
export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
