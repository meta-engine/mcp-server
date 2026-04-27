import { Id } from '../../../shared/value-objects/id';

/** CartLine value object. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
