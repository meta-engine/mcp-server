package com.metaengine.demo.analytics.services;

import com.metaengine.demo.analytics.aggregates.Event;
import java.util.List;

/** Persistence gateway for analytics events. */
public class EventRepository {
    /** Persist a new event from the provided partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Load an event by id. Returns null when not found. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List up to {@code limit} events. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Remove an event by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
