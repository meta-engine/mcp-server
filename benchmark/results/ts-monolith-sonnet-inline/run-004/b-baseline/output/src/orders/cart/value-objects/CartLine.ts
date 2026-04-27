import { Id } from '../../../shared/value-objects/Id';

/** Single product line in a shopping cart */
export interface CartLine {
  productId: Id;
  quantity: number;
}
