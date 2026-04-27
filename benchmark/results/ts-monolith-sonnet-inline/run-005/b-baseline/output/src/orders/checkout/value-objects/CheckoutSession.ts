import { Id } from '../../../shared/value-objects/Id';

/** Represents an active checkout session linking cart, customer, and shipping method. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
