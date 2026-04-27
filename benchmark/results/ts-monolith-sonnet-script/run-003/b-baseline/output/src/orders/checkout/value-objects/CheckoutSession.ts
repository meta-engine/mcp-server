import { Id } from '../../../shared/value-objects/Id';

/** CheckoutSession value object */
export interface CheckoutSession {
  readonly cartId: Id;
  readonly customerId: Id;
  readonly shippingMethodId: Id;
}
