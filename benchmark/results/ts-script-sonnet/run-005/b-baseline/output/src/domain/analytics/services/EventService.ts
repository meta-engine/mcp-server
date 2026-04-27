import { Event } from '../aggregates/Event';

/** Application service for managing analytics event operations. */
export class EventService {
  create(input: Partial<Event>): Event {
    void input;
    throw new Error('not implemented');
  }

  findById(id: string): Event | null {
    void id;
    throw new Error('not implemented');
  }

  list(limit: number): Event[] {
    void limit;
    throw new Error('not implemented');
  }

  delete(id: string): void {
    void id;
    throw new Error('not implemented');
  }
}
