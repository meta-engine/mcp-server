package com.metaengine.demo.analytics.services;

import java.util.List;

import com.metaengine.demo.analytics.aggregates.Event;

/** EventRepository persistence service. */
public class EventRepository {

    /** Persist an Event from a partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Event by id (may return null). */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List events up to limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Event by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
