import { Id } from "../../../shared/value-objects/Id";

/** A user's in-progress checkout. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
