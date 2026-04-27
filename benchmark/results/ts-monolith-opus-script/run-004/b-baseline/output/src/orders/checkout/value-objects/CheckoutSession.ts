import { Id } from "../../../shared/value-objects/Id";

/** CheckoutSession value object. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
