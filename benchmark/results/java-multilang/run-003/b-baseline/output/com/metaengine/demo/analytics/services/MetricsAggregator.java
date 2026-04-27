package com.metaengine.demo.analytics.services;

import com.metaengine.demo.analytics.aggregates.Event;
import java.util.List;

/** MetricsAggregator domain service for the analytics domain. */
public class MetricsAggregator {
    /** Create a new Event from a partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Event by its identifier. May return null. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Events up to the given limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Event by its identifier. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
