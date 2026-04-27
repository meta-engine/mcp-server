import { Id } from '../../../shared/value-objects/Id';

/** A product line within a shopping cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
