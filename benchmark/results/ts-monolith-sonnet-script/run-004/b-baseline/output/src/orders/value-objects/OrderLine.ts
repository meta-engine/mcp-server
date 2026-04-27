import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';

/** OrderLine value object representing a single line in an order. */
export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
