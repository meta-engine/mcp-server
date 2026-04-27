import { Id } from '../../../shared/value-objects/Id';

/** CartLine value object representing a single product in the cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
