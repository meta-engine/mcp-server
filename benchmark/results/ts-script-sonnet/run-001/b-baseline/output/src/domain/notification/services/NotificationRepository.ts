import { Notification } from '../aggregates/Notification';

/** NotificationRepository service. */
export class NotificationRepository {
  create(input: Partial<Notification>): Notification { throw new Error('not implemented'); }
  findById(id: string): Notification | null { throw new Error('not implemented'); }
  list(limit: number): Notification[] { throw new Error('not implemented'); }
  delete(id: string): void { throw new Error('not implemented'); }
}
