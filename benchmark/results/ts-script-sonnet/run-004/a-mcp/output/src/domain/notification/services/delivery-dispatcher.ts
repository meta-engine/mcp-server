import { Notification } from '../aggregates/notification';

/** DeliveryDispatcher service. */
export class DeliveryDispatcher {

  create(input: Partial<Notification>): Notification { throw new Error('not implemented'); }

  findById(id: string): Notification | null { throw new Error('not implemented'); }

  list(limit: number): Notification[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
