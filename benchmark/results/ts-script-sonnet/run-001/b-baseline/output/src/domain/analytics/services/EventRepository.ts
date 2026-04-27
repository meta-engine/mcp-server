import { Event } from '../aggregates/Event';

/** EventRepository service. */
export class EventRepository {
  create(input: Partial<Event>): Event { throw new Error('not implemented'); }
  findById(id: string): Event | null { throw new Error('not implemented'); }
  list(limit: number): Event[] { throw new Error('not implemented'); }
  delete(id: string): void { throw new Error('not implemented'); }
}
