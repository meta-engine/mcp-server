package com.metaengine.demo.analytics.services;

import java.util.List;

import com.metaengine.demo.analytics.aggregates.Event;

/** MetricsAggregator for the analytics domain. */
public class MetricsAggregator {

    /** Create a new Event from partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Event by id. Returns null if not found. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Events up to the given limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete the Event with the given id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
