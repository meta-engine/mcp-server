import { Id } from "../../shared/value-objects/Id";
import { Money } from "../../shared/value-objects/Money";

/** A single line in an Order. */
export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
