import { Id } from '../../../shared/value-objects/Id';

/** CheckoutSession value object capturing cart and customer for checkout. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
