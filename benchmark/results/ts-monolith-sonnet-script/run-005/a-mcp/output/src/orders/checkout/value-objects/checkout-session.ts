import { Id } from '../../../shared/value-objects/id';

export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
