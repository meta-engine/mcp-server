package com.metaengine.demo.analytics.services;

import com.metaengine.demo.analytics.aggregates.Event;
import java.util.List;

/** Domain service that rolls events up into aggregated metrics. */
public class MetricsAggregator {
    /** Aggregate metrics from the event described by the partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Look up an aggregated event by id. Returns null when not found. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} aggregated events. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove aggregated metrics for the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
