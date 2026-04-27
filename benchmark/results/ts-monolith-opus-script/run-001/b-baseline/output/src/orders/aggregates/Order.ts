import { Id } from '../../shared/value-objects/Id';
import { OrderStatus } from '../enums/OrderStatus';
import { OrderTotal } from '../value-objects/OrderTotal';

/** Order aggregate representing a customer's purchase order. */
export class Order {
  constructor(
    public readonly id: Id,
    public readonly customerId: Id,
    public readonly status: OrderStatus,
    public readonly total: OrderTotal,
  ) {}
}
