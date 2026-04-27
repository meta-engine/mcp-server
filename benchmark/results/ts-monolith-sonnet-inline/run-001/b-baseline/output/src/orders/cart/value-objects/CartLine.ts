import { Id } from '../../../shared/value-objects/Id';

/** Represents a single line item in a cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
