import { Id } from "../../../shared/value-objects/Id";
import { CartState } from "../enums/CartState";

/** Shopping cart aggregate. */
export class Cart {
  constructor(
    public readonly id: Id,
    public readonly customerId: Id,
    public readonly state: CartState,
  ) {}
}
