import { Id } from "../../../shared/value-objects/Id";

/** A line item within a cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
