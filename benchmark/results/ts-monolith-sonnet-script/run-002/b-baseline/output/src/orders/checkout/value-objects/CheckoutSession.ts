import { Id } from '../../../shared/value-objects/Id';

/** Snapshot of a checkout session linking cart, customer, and shipping. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
