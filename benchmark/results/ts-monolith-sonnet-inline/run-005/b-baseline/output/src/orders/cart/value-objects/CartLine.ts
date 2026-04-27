import { Id } from '../../../shared/value-objects/Id';

/** A single product entry in a shopping cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
