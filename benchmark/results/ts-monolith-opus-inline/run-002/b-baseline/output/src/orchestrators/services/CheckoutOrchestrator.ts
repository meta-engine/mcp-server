import { Id } from "../../shared/value-objects/Id";
import { Money } from "../../shared/value-objects/Money";
import { Result } from "../../shared/value-objects/Result";
import { PaymentMethod } from "../../customers/value-objects/PaymentMethod";
import { Cart } from "../../orders/cart/aggregates/Cart";
import { Order } from "../../orders/aggregates/Order";

/** CheckoutOrchestrator service. */
export class CheckoutOrchestrator {
  placeOrder(cartId: Id, customerId: Id, paymentMethodId: PaymentMethod): Order {
    void cartId;
    void customerId;
    void paymentMethodId;
    throw new Error("not implemented");
  }
  validateCart(cart: Cart): Result {
    void cart;
    throw new Error("not implemented");
  }
  computeTotal(cart: Cart): Money {
    void cart;
    throw new Error("not implemented");
  }
}
