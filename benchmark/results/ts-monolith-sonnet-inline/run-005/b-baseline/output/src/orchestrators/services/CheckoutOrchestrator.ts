import { Id } from '../../shared/value-objects/Id';
import { Money } from '../../shared/value-objects/Money';
import { Result } from '../../shared/value-objects/Result';
import { PaymentMethod } from '../../customers/value-objects/PaymentMethod';
import { Order } from '../../orders/aggregates/Order';
import { Cart } from '../../orders/cart/aggregates/Cart';

/** Orchestrates the full checkout flow across cart, orders, and billing modules. */
export class CheckoutOrchestrator {
  placeOrder(cartId: Id, customerId: Id, paymentMethodId: PaymentMethod): Order { throw new Error('not implemented'); }
  validateCart(cart: Cart): Result { throw new Error('not implemented'); }
  computeTotal(cart: Cart): Money { throw new Error('not implemented'); }
}
