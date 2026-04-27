import { Id } from '../../../shared/value-objects/Id';

/** Represents an active checkout session. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
