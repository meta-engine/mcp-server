import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';

/** Single line item within an order */
export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
