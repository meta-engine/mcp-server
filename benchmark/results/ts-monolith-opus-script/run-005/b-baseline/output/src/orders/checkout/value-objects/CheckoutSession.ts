import { Id } from "../../../shared/value-objects/Id";

/** A customer's checkout session snapshot. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
