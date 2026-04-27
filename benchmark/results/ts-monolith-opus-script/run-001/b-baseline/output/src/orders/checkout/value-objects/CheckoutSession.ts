import { Id } from '../../../shared/value-objects/Id';

/** CheckoutSession value object representing an active checkout flow. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
