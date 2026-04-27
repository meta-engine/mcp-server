import { PaymentMethod } from '../../customers/value-objects/payment-method';
import { Order } from '../../orders/aggregates/order';
import { Id } from '../../shared/value-objects/id';
import { Result } from '../../shared/value-objects/result';
import { Cart } from '../../orders/cart/aggregates/cart';
import { Money } from '../../shared/value-objects/money';

export class CheckoutOrchestrator {

  placeOrder(cartId: Id, customerId: Id, paymentMethodId: PaymentMethod): Order { throw new Error('not implemented'); }

  validateCart(cart: Cart): Result { throw new Error('not implemented'); }

  computeTotal(cart: Cart): Money { throw new Error('not implemented'); }
}
