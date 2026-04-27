import { Event } from '../aggregates/Event';

/** Aggregator for computing and summarising analytics metrics from events. */
export class MetricsAggregator {
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
