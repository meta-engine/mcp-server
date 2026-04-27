import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';

/** Represents a single line item in an order. */
export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
