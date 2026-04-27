import { Id } from '../../../shared/value-objects/Id';

/** Value object capturing the inputs for a checkout session. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
