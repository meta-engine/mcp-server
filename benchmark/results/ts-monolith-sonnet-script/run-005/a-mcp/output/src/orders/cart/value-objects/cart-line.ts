import { Id } from '../../../shared/value-objects/id';

export interface CartLine {
  productId: Id;
  quantity: number;
}
