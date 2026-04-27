import { AnalyticsEvent } from '../aggregates/event';

/** EventRepository service. */
export class EventRepository {

  create(input: Partial<AnalyticsEvent>): AnalyticsEvent { throw new Error('not implemented'); }

  findById(id: string): AnalyticsEvent | null { throw new Error('not implemented'); }

  list(limit: number): AnalyticsEvent[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
