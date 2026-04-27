import { Notification } from '../aggregates/notification';

export class NotificationService {

  create(input: Partial<Notification>): Notification { throw new Error('not implemented'); }

  findById(id: string): Notification | null { throw new Error('not implemented'); }

  list(limit: number): Notification[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
