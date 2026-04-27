import { Id } from '../../shared/value-objects/id';
import { Money } from '../../shared/value-objects/money';

export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
