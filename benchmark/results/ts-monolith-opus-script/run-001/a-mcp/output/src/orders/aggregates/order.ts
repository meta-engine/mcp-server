import { Id } from '../../shared/value-objects/id';
import { OrderStatus } from '../enums/order-status.enum';
import { OrderTotal } from '../value-objects/order-total';

export class Order {

  constructor(public id: Id, public customerId: Id, public status: OrderStatus, public total: OrderTotal) { }
}
