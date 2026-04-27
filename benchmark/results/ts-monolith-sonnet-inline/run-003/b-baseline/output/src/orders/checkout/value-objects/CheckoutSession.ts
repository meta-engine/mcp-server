import { Id } from '../../../shared/value-objects/Id';

/** Active checkout session linking cart, customer, and shipping. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
