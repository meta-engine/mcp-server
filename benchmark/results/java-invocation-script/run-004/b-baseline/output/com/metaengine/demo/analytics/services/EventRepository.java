package com.metaengine.demo.analytics.services;

import com.metaengine.demo.analytics.aggregates.Event;
import java.util.List;

/** EventRepository persistence service in the analytics domain. */
public class EventRepository {
    /** Persist a new Event from a partial input. */
    public Event create(Event input) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Find an Event by id, or null if not found. */
    public Event findById(String id) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** List Events up to limit. */
    public List<Event> list(int limit) {
        throw new UnsupportedOperationException("not implemented");
    }

    /** Delete an Event by id. */
    public void delete(String id) {
        throw new UnsupportedOperationException("not implemented");
    }
}
