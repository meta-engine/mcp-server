import { Id } from '../../shared/value-objects/Id';
import { OrderStatus } from '../enums/OrderStatus';
import { OrderTotal } from '../value-objects/OrderTotal';

/** Order aggregate tracking a customer's purchase from placement to delivery. */
export class Order {
  constructor(
    public readonly id: Id,
    public readonly customerId: Id,
    public readonly status: OrderStatus,
    public readonly total: OrderTotal,
  ) {}
}
