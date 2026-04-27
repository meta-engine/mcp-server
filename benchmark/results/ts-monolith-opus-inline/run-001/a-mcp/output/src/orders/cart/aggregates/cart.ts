import { Id } from '../../../shared/value-objects/id';
import { CartState } from '../enums/cart-state.enum';

/** Cart aggregate root for the orders.cart module. */
export class Cart {

  constructor(public id: Id, public customerId: Id, public state: CartState) { }
}
