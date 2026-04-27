import { Id } from '../../../shared/value-objects/Id';

/** Active checkout session tying cart, customer and shipping together */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
