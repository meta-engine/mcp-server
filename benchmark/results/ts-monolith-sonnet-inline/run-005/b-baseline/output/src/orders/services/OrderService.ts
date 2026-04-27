import { Id } from '../../shared/value-objects/Id';
import { Order } from '../aggregates/Order';

/** Manages order lifecycle in the orders module. */
export class OrderService {
  create(input: Partial<Order>): Order { throw new Error('not implemented'); }
  findById(id: Id): Order | null { throw new Error('not implemented'); }
  list(limit: number): Order[] { throw new Error('not implemented'); }
  delete(id: Id): void { throw new Error('not implemented'); }
}
