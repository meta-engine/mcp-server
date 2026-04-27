import { Id } from '../../../shared/value-objects/Id';

/** Transient session capturing checkout intent. */
export interface CheckoutSession {
  cartId: Id;
  customerId: Id;
  shippingMethodId: Id;
}
