import { Id } from '../../../shared/value-objects/Id';

/** An active checkout session binding cart, customer, and shipping method. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
