import { Order } from '../aggregates/order';
import { Id } from '../../shared/value-objects/id';

export class OrderService {

  create(input: Partial<Order>): Order { throw new Error('not implemented'); }

  findById(id: Id): Order | null { throw new Error('not implemented'); }

  list(limit: number): Order[] { throw new Error('not implemented'); }

  delete(id: Id): void { throw new Error('not implemented'); }
}
