import { Id } from '../../../shared/value-objects/id';

/** CheckoutSession value object. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
