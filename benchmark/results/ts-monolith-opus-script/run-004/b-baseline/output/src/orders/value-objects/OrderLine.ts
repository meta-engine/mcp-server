import { Id } from "../../shared/value-objects/Id";
import { Money } from "../../shared/value-objects/Money";

/** OrderLine value object. */
export interface OrderLine {
  productId: Id;
  quantity: number;
  unitPrice: Money;
}
