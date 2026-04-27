import { Id } from '../../../shared/value-objects/Id';

/** CartLine value object representing a single item in a cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
