import { Id } from "../../../shared/value-objects/Id";

/** A single line item in a Cart. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
