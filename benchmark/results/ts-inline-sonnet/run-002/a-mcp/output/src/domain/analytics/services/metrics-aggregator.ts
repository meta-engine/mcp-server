import { AnalyticsEvent } from '../aggregates/event';

/** MetricsAggregator service. */
export class MetricsAggregator {

  create(input: Partial<AnalyticsEvent>): AnalyticsEvent { throw new Error('not implemented'); }

  findById(id: string): AnalyticsEvent | null { throw new Error('not implemented'); }

  list(limit: number): AnalyticsEvent[] { throw new Error('not implemented'); }

  delete(id: string): void { throw new Error('not implemented'); }
}
