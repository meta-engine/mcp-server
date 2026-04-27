import { Id } from "../../../shared/value-objects/Id";

/** Active checkout session for a cart. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
