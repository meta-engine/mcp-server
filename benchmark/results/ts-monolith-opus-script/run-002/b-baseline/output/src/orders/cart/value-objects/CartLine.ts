import { Id } from "../../../shared/value-objects/Id";

/** Single product line within a cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
