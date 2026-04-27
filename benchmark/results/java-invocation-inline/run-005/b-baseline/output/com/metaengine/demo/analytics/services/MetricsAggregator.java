package com.metaengine.demo.analytics.services;

import com.metaengine.demo.analytics.aggregates.Event;
import java.util.List;

/** Aggregates Event data into metrics. */
public class MetricsAggregator {

    /** Create a new aggregated Event from a partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an aggregated Event by id; returns null if not found. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List aggregated Events, capped at the supplied limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an aggregated Event by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
