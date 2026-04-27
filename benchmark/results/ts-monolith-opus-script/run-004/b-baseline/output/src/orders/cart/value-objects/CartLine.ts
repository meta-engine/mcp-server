import { Id } from "../../../shared/value-objects/Id";

/** CartLine value object. */
export interface CartLine {
  productId: Id;
  quantity: number;
}
