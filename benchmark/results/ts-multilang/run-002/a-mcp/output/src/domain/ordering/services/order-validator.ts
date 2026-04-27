import { Order } from '../aggregates/order';

/** OrderValidator service. */
export class OrderValidator {

  create(input: Partial<Order>): Order { throw new Error('not implemented'); }

  findById(id: string): Order | null { throw new Error('not implemented'); }

  list(limit: number): Order[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
