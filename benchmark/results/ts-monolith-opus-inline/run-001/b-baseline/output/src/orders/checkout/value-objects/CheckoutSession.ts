import { Id } from "../../../shared/value-objects/Id";

/** A checkout session linking a cart, customer and shipping option. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
